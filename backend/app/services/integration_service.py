"""Orchestrate all export and integration tasks"""
import io
from fastapi import Response
from backend.app.modules.module_12_exporter import (
    ZIPExporter, DashboardGenerator, JiraConnector, GitConnector, SlackConnector
)
from backend.app.services.document_service import DocumentService
from backend.app.services.uml_service import UMLService
from backend.app.database.models import Project, Requirement, Diagram
from sqlalchemy.orm import Session
from typing import Dict, Any

class IntegrationService:
    @staticmethod
    async def export_project_zip(project_db_id: int, db: Session) -> bytes:
        """Generate ZIP containing all documents and UML diagrams as PNG"""
        # Get documents as PDF bytes
        docs_html = DocumentService.generate_all_documents(project_db_id, db)
        doc_pdfs = {}
        for doc_type, html in docs_html.items():
            pdf_bytes = DocumentService.html_to_pdf(html)
            if pdf_bytes:
                doc_pdfs[doc_type] = pdf_bytes
        
        # Get UML diagrams as PNG bytes
        diagrams = db.query(Diagram).filter(Diagram.project_id == project_db_id).all()
        diagram_images = {}
        for diag in diagrams:
            png_bytes = UMLService.render_diagram_image(diag.id, db, "png")
            if png_bytes and not isinstance(png_bytes, dict):
                diagram_images[f"{diag.diagram_type}_{diag.id}"] = png_bytes
        
        # Get project object for project_id string
        project = db.query(Project).filter(Project.id == project_db_id).first()
        project_id_str = project.project_id if project else "unknown"
        zip_buffer = ZIPExporter.create_export_zip(project_id_str, doc_pdfs, diagram_images)
        return zip_buffer.getvalue()
    
    @staticmethod
    async def generate_dashboard(project_db_id: int, db: Session) -> str:
        """Generate interactive HTML dashboard"""
        project = db.query(Project).filter(Project.id == project_db_id).first()
        if not project:
            return "<html><body>Project not found</body></html>"
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        
        # Aggregate data
        priority_counts = {"MUST": 0, "SHOULD": 0, "COULD": 0, "WONT": 0}
        rqi_dist = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        total_effort = sum(r.effort_hours or 0 for r in requirements)
        avg_rqi = sum(r.quality_score or 0 for r in requirements) / max(1, len(requirements))
        
        for r in requirements:
            priority_value = r.priority.value if hasattr(r.priority, 'value') else str(r.priority).upper()
            priority_counts[priority_value] = priority_counts.get(priority_value, 0) + 1
            if r.quality_score:
                if r.quality_score >= 85:
                    rqi_dist["excellent"] += 1
                elif r.quality_score >= 70:
                    rqi_dist["good"] += 1
                elif r.quality_score >= 50:
                    rqi_dist["fair"] += 1
                else:
                    rqi_dist["poor"] += 1
        
        req_list = []
        for r in requirements:
            req_list.append({
                "id": r.requirement_id,
                "text": r.text,
                "priority": r.priority.value if hasattr(r.priority, 'value') else str(r.priority),
                "rqi_score": r.quality_score
            })
        
        project_data = {
            "project_id": project.project_id,
            "requirements": req_list,
            "priority_distribution": priority_counts,
            "rqi_distribution": rqi_dist,
            "total_effort_hours": total_effort,
            "avg_rqi": round(avg_rqi, 1)
        }
        return DashboardGenerator.generate(project_data)
    
    @staticmethod
    async def push_to_jira(project_db_id: int, db: Session) -> Dict:
        """Push requirements to Jira using user-specific settings"""
        project = db.query(Project).filter(Project.id == project_db_id).first()
        if not project:
            return {"error": "Project not found"}
        
        # Fetch user settings for credentials
        from backend.app.database.models import UserSettings
        settings = db.query(UserSettings).filter(UserSettings.user_id == project.user_id).first()
        
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        req_list = [{"requirement_id": r.requirement_id, "text": r.text, "category": r.category} for r in requirements]
        connector = JiraConnector(settings=settings)
        result = connector.push_requirements(req_list, project.name)
        return result
    
    @staticmethod
    async def push_to_git(project_db_id: int, db: Session) -> Dict:
        """Push documentation to GitHub using user-specific settings"""
        project = db.query(Project).filter(Project.id == project_db_id).first()
        if not project:
            return {"error": "Project not found"}
        
        # Fetch user settings for credentials
        from backend.app.database.models import UserSettings
        settings = db.query(UserSettings).filter(UserSettings.user_id == project.user_id).first()
            
        docs_html = DocumentService.generate_all_documents(project.id, db)
        connector = GitConnector(settings=settings)
        repo_name = f"docuforge-{project.project_id.lower()}"
        result = connector.push_documentation(repo_name, docs_html)
        return result
    
    @staticmethod
    async def send_slack_notification(project_db_id: int, db: Session, message: str = None) -> Dict:
        """Send Slack notification about project generation"""
        project = db.query(Project).filter(Project.id == project_db_id).first()
        if not project:
            return {"error": "Project not found"}
        
        # Optionally use Slack webhook from settings
        from backend.app.database.models import UserSettings
        settings = db.query(UserSettings).filter(UserSettings.user_id == project.user_id).first()
        
        connector = SlackConnector() # SlackConnector could also be updated but it's simpler
        if not message:
            message = f"Project `{project.project_id}` documentation has been generated successfully."
        result = connector.send_notification(message, project.project_id)
        return result