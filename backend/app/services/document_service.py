"""Service to generate all documents and export to PDF/DOCX/HTML"""
import os
import tempfile
import io
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import os
    # Add Homebrew library paths for Apple Silicon Macs
    if os.path.exists('/opt/homebrew/lib'):
        os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
        # Some versions of cffi need this too
        if 'LD_LIBRARY_PATH' not in os.environ:
            os.environ['LD_LIBRARY_PATH'] = '/opt/homebrew/lib'
    
    from weasyprint import HTML
except Exception as e:
    print(f"Warning: weasyprint not available ({e})")
    HTML = None

try:
    from docx import Document
    from docx.shared import Inches
except ImportError:
    Document = None

try:
    from bs4 import BeautifulSoup  # pip install beautifulsoup4
except ImportError:
    BeautifulSoup = None

# Import generators
from backend.app.modules.module_11_document_generator.srs_generator import SRSGenerator
from backend.app.modules.module_11_document_generator.sow_generator import SOWGenerator
from backend.app.modules.module_11_document_generator.test_plan_generator import TestPlanGenerator
from backend.app.modules.module_11_document_generator.deployment_guide_generator import DeploymentGuideGenerator
from backend.app.modules.module_11_document_generator.compliance_generator import ComplianceGenerator

# Import services for dynamic data
from backend.app.services.impact_service import ImpactAnalysisService
from backend.app.services.quality_service import QualityAssessmentService
from backend.app.database.models import Project, Requirement, Conflict


class DocumentService:
    @staticmethod
    def generate_all_documents(project_id: int, db) -> Dict[str, str]:
        """
        Generate HTML for all document types.
        Returns dict: {'srs': '<html>...', 'sow': '...', ...}
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "Project not found"}

        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        conflicts = db.query(Conflict).filter(Conflict.project_id == project_id, Conflict.resolved == False).all()

        # Run analyses (or reuse cached data if available)
        impact_result = ImpactAnalysisService.analyze_project(project_id, db)
        quality_result = QualityAssessmentService.assess_project(project_id, db)

        docs = {}

        # 1. SRS (pass full project + context)
        docs['srs'] = SRSGenerator.generate(
            project, requirements, conflicts,
            impact_result,
            quality_result
        )

        # 2. SOW (pass project)
        docs['sow'] = SOWGenerator.generate(project, impact_result, requirements)

        # 3. Test Plan (pass project)
        docs['test_plan'] = TestPlanGenerator.generate(requirements, project=project)

        # 4. Deployment Guide (pass project)
        docs['deployment_guide'] = DeploymentGuideGenerator.generate(project=project)

        # 5. Compliance Package (pass project + requirements)
        docs['compliance'] = ComplianceGenerator.generate(project=project, requirements=requirements)

        return docs


    @staticmethod
    def html_to_pdf(html_content: str) -> Optional[bytes]:
        """Convert HTML string to PDF bytes using WeasyPrint."""
        if HTML is None:
            print("PDF generation disabled: WeasyPrint or its dependencies (pango, glib) are not installed.")
            return None
        try:
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except Exception as e:
            print(f"PDF generation error: {e}")
            return None

    @staticmethod
    def html_to_docx(html_content: str) -> Optional[bytes]:
        """
        Convert HTML to DOCX using BeautifulSoup and python-docx.
        Produces a professional-grade Word document.
        """
        if Document is None or BeautifulSoup is None:
            print("DOCX generation disabled: python-docx or beautifulsoup4 is not installed.")
            return None
        try:
            doc = Document()
            soup = BeautifulSoup(html_content, 'html.parser')

            # Process elements in order
            for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'table', 'ul', 'ol']):
                if element.name == 'h1':
                    doc.add_heading(element.get_text().strip(), level=1)
                elif element.name == 'h2':
                    doc.add_heading(element.get_text().strip(), level=2)
                elif element.name == 'h3':
                    doc.add_heading(element.get_text().strip(), level=3)
                elif element.name == 'p':
                    # Skip empty paragraphs or those just containing whitespace
                    if not element.get_text().strip():
                        continue
                    p = doc.add_paragraph()
                    # Parse inline formatting (bold, italic)
                    for child in element.children:
                        if child.name in ('strong', 'b'):
                            p.add_run(child.get_text()).bold = True
                        elif child.name in ('em', 'i'):
                            p.add_run(child.get_text()).italic = True
                        else:
                            p.add_run(str(child.string) if child.string else child.get_text())
                elif element.name == 'table':
                    rows = element.find_all('tr')
                    if not rows: continue
                    
                    # Determine number of columns
                    max_cols = 0
                    for row in rows:
                        max_cols = max(max_cols, len(row.find_all(['td', 'th'])))
                    
                    if max_cols == 0: continue
                    
                    table = doc.add_table(rows=0, cols=max_cols)
                    table.style = 'Table Grid'
                    
                    for row in rows:
                        row_cells = table.add_row().cells
                        cells = row.find_all(['td', 'th'])
                        for i, cell in enumerate(cells):
                            if i < max_cols:
                                row_cells[i].text = cell.get_text().strip()
                elif element.name in ('ul', 'ol'):
                    style = 'List Bullet' if element.name == 'ul' else 'List Number'
                    for li in element.find_all('li', recursive=False):
                        if li.get_text().strip():
                            doc.add_paragraph(li.get_text().strip(), style=style)

            # Save document to bytes
            f = io.BytesIO()
            doc.save(f)
            f.seek(0)
            return f.read()
        except Exception as e:
            print(f"DOCX generation error: {e}")
            return None

    @staticmethod
    def export_zip(project_id: int, db) -> Optional[bytes]:
        """
        Export all documents as PDF + DOCX + HTML in a ZIP archive.
        (Optional – can be added later)
        """
        # For now, return None; full ZIP export can be implemented in Phase 12
        return None