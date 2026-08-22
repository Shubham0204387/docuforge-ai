"""Service to formalize requirements using Module 5"""
from backend.app.modules.module_5_requirement_generator import (
    FormalConverter, IDGenerator, Classifier
)
from backend.app.database.models import Requirement, Project, Priority
from sqlalchemy.orm import Session
from typing import List, Dict

class FormalizationService:
    """Orchestrates formal requirement generation"""
    
    def __init__(self):
        self.id_gen = IDGenerator()
    
    def formalize_requirement(self, req_text: str, req_type: str = "functional") -> Dict:
        """Convert a single requirement to formal IEEE 830 format with all metadata"""
        # Convert to formal language
        formal_text = FormalConverter.convert(req_text, req_type)
        
        # Classify priority and category
        classification = Classifier.classify_full(formal_text, req_type)
        
        return {
            "original_text": req_text,
            "formal_text": formal_text,
            "priority": classification["priority"],
            "priority_confidence": classification["priority_confidence"],
            "category": classification["category"],
            "testability_score": classification["testability_score"],
            "testability_level": classification["testability_level"]
        }
    
    def formalize_project_requirements(self, project_id: int, db: Session) -> Dict:
        """Convert all informal requirements in a project to formal ones"""
        # Get existing requirements
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        
        if not requirements:
            return {"message": "No requirements found", "formalized_count": 0}
        
        # Get existing IDs for counter sync
        existing_ids = [r.requirement_id for r in requirements]
        self.id_gen.reset()
        self.id_gen._sync_counters(existing_ids)
        
        formalized_count = 0
        results = []
        
        for req in requirements:
            # Skip already formalized? (you can decide to update or skip)
            # For now, we'll update all to ensure formal format
            formal_text = FormalConverter.convert(req.text, req.type)
            
            # Classify if not already classified
            if not req.category or req.priority_confidence == 0:
                classification = Classifier.classify_full(req.text, req.type)
                req.category = classification["category"]
                req.priority = classification["priority"]
                req.priority_confidence = classification["priority_confidence"]
                # Update text to formal version
                req.text = formal_text
                formalized_count += 1
                results.append({
                    "requirement_id": req.requirement_id,
                    "original": req.text,
                    "formal": formal_text,
                    "priority": req.priority,
                    "category": req.category
                })
            else:
                # Still update text to formal
                req.text = formal_text
                formalized_count += 1
        
        db.commit()
        
        # Get project for response
        project = db.query(Project).filter(Project.id == project_id).first()
        
        return {
            "project_id": project.project_id if project else str(project_id),
            "requirements_processed": len(requirements),
            "formalized_count": formalized_count,
            "examples": results[:5]  # Return first 5 examples
        }
    
    def generate_new_formal_requirements(self, expanded_reqs: List[Dict], project_id: int, db: Session) -> List[Dict]:
        """Generate formal requirements from expanded list and save to database"""
        from backend.app.database.models import Requirement, Priority as PriorityEnum
        
        # Get existing IDs
        existing = db.query(Requirement.requirement_id).filter(Requirement.project_id == project_id).all()
        existing_ids = [e[0] for e in existing]
        self.id_gen.reset()
        self.id_gen._sync_counters(existing_ids)
        
        saved = []
        for exp_req in expanded_reqs:
            text = exp_req.get('text', '')
            confidence = exp_req.get('confidence', 0.7)
            source = exp_req.get('source_rule', 'inference')
            category = exp_req.get('category', 'General')
            
            # Determine requirement type based on content
            if "PCI" in text or "encrypt" in text.lower():
                req_type = "non_functional"
            elif "comply" in text.lower() or "gdpr" in text.lower():
                req_type = "constraint"
            else:
                req_type = "functional"
            
            # Convert to formal
            formal_text = FormalConverter.convert(text, req_type)
            
            # Classify priority
            priority_result = Classifier.classify_priority(formal_text)
            priority_map = {"MUST": PriorityEnum.MUST, "SHOULD": PriorityEnum.SHOULD,
                           "COULD": PriorityEnum.COULD, "WONT": PriorityEnum.WONT}
            priority_enum = priority_map.get(priority_result["priority"], PriorityEnum.SHOULD)
            
            # Generate ID
            req_id = self.id_gen.generate_id(req_type, existing_ids)
            existing_ids.append(req_id)
            
            # Create requirement in DB
            new_req = Requirement(
                requirement_id=req_id,
                text=formal_text,
                type=req_type,
                category=category,
                priority=priority_enum,
                priority_confidence=priority_result["confidence"],
                source=source,
                project_id=project_id
            )
            db.add(new_req)
            saved.append({
                "requirement_id": req_id,
                "formal_text": formal_text,
                "priority": priority_result["priority"],
                "category": category
            })
        
        db.commit()
        return saved
