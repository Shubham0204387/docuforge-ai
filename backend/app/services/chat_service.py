from sqlalchemy.orm import Session
from backend.app.database.models import Project, Requirement, Diagram
from backend.app.core.ai_client import ai_client
from typing import List, Dict

class ChatService:
    @staticmethod
    def get_project_context(project_id: str, db: Session) -> str:
        """Gather all project data to provide context to the AI"""
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            return "Project not found."
            
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        req_text = "\n".join([f"- [{r.requirement_id}] {r.text} ({r.priority})" for r in requirements])
        
        context = f"""
Project Name: {project.name}
Domain: {project.domain}
Raw Input: {project.raw_input[:500]}...

Requirements:
{req_text}
"""
        return context

    @staticmethod
    def ask_question(project_id: str, question: str, db: Session) -> str:
        context = ChatService.get_project_context(project_id, db)
        
        system_prompt = f"""
You are DocuForge AI Assistant, an expert Requirements Engineer.
Below is the context of the current project. Answer the user's question accurately based on this documentation.
If the question is about missing requirements, suggest 2-3 specific ones.
If the question is about conflicts, analyze the existing requirements.

PROJECT CONTEXT:
{context}
"""
        return ai_client.get_completion(system_prompt, question)
