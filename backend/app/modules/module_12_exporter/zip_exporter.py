"""Create ZIP archive containing all generated documents and UML diagrams"""
import io
import zipfile
import os
from typing import Dict, Optional, List
from datetime import datetime

class ZIPExporter:
    @staticmethod
    def create_export_zip(project_id: str, documents: Dict[str, bytes], diagrams: Dict[str, bytes]) -> io.BytesIO:
        """
        Create a ZIP archive with all project deliverables.
        - documents: dict mapping doc_type -> bytes (PDF or DOCX)
        - diagrams: dict mapping diagram_name -> bytes (PNG)
        Returns BytesIO of the ZIP file.
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add documents
            for doc_type, content in documents.items():
                zip_file.writestr(f"documents/{doc_type}.pdf", content)
            
            # Add diagrams
            for diagram_name, content in diagrams.items():
                zip_file.writestr(f"diagrams/{diagram_name}.png", content)
            
            # Add a README file
            readme = f"""DocuForge AI Export – Project {project_id}
Generated on {datetime.now().isoformat()}

Contents:
- documents/ : all generated documents (SRS, SOW, test plan, deployment guide, compliance)
- diagrams/  : UML diagrams (use case, class, sequence, activity)

For more information, visit https://docuforge.ai
"""
            zip_file.writestr("README.txt", readme)
        
        zip_buffer.seek(0)
        return zip_buffer
