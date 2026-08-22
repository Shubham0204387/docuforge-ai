"""Service to integrate Module 4 with the rest of the system"""
from backend.app.modules.module_4_knowledge_graph import KnowledgeBaseLoader, RuleApplicator
from backend.app.database.models import Requirement, Project, RequirementType, Priority  # ADD THIS
from sqlalchemy.orm import Session
from typing import List, Dict
import re

class InferenceService:
    """Orchestrates knowledge graph operations for a project"""
    
    def __init__(self):
        self.loader = KnowledgeBaseLoader()
    
    def expand_project_requirements(self, project_id: int, db: Session) -> Dict:
        """Expand all requirements for a project using inference rules"""
        # Get existing requirements
        existing_reqs = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        req_list = [{"id": r.id, "text": r.text} for r in existing_reqs]
        
        # Get project domain
        project = db.query(Project).filter(Project.id == project_id).first()
        domain = project.domain if project else "general"
        
        # Get rules
        rules = self.loader.get_rules(domain)
        
        # Apply rules
        result = RuleApplicator.apply_all(req_list, domain, rules)
        
        # Save new requirements to database (with unique IDs)
        # Get current max requirement ID number
        existing_ids = db.query(Requirement.requirement_id).filter(Requirement.project_id == project_id).all()
        id_numbers = [int(re.search(r'\d+', e[0]).group()) for e in existing_ids if re.search(r'\d+', e[0])]
        next_id = max(id_numbers) + 1 if id_numbers else 1
        
        added_count = 0
        for new_req in result['expanded_requirements']:
            # Check if already exists (by text similarity)
            exists = False
            for existing in existing_reqs:
                if existing.text.lower() == new_req['text'].lower():
                    exists = True
                    break
            if not exists:
                req = Requirement(
                    requirement_id=f"INF_{next_id:03d}",
                    text=new_req['text'],
                    type="functional",
                    category=new_req.get('category', 'Inferred'),
                    priority=Priority.SHOULD,
                    priority_confidence=new_req.get('confidence', 0.7),
                    source="inference_engine",
                    project_id=project_id
                )
                db.add(req)
                next_id += 1
                added_count += 1
        
        db.commit()
        
        return {
            "project_id": project.project_id,
            "original_requirements": len(existing_reqs),
            "added_requirements": added_count,
            "applied_rules": result['applied_rules'],
            "new_requirements": result['expanded_requirements'][:10]
        }
    
    def expand_single_text(self, text: str, domain: str) -> Dict:
        """Expand a single text without database persistence"""
        rules = self.loader.get_rules(domain)
        req_list = [{"id": 1, "text": text}]
        result = RuleApplicator.apply_all(req_list, domain, rules)
        return result
