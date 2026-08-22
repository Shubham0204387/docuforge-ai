"""Service to orchestrate conflict detection across all requirements"""
from backend.app.modules.module_6_conflict_detector import (
    SemanticConflictAnalyzer, ResourceConflictChecker,
    PriorityDeadlockFinder, ResolutionSuggester
)
from backend.app.database.models import Conflict, ConflictSeverity, Requirement, Project
from sqlalchemy.orm import Session
from typing import List, Dict

class ConflictDetectionService:
    """Runs all conflict detectors and stores results"""
    
    @classmethod
    def detect_all_conflicts(cls, project_id: int, db: Session) -> Dict:
        """Detect conflicts for all requirements in a project and store in DB"""
        # Fetch requirements
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        if not requirements:
            return {"message": "No requirements found", "conflicts_detected": 0}
        
        # Build list for detectors: use requirement_id string for identification
        req_list = [{"requirement_id": r.requirement_id, "text": r.text, "db_id": r.id} for r in requirements]
        
        # Run detectors (they return requirement_id strings)
        semantic = SemanticConflictAnalyzer.detect_conflicts(req_list)
        resource = ResourceConflictChecker.detect_conflicts(req_list)
        deadlocks = PriorityDeadlockFinder.find_deadlocks(req_list)
        
        all_conflicts = semantic + resource + deadlocks
        
        # Store conflicts in database (avoid duplicates)
        stored = []
        for conf in all_conflicts:
            # Find the actual database IDs for the two requirements
            req1_str = conf.get('requirement_1')
            req2_str = conf.get('requirement_2')
            req1 = db.query(Requirement).filter(Requirement.requirement_id == req1_str, Requirement.project_id == project_id).first()
            req2 = db.query(Requirement).filter(Requirement.requirement_id == req2_str, Requirement.project_id == project_id).first()
            if not req1 or not req2:
                continue  # skip if not found
            
            # Check if conflict already exists
            existing = db.query(Conflict).filter(
                Conflict.project_id == project_id,
                Conflict.requirement_id_1 == req1.id,
                Conflict.requirement_id_2 == req2.id,
                Conflict.conflict_type == conf.get('type')
            ).first()
            if not existing:
                severity_map = {"CRITICAL": ConflictSeverity.CRITICAL, "HIGH": ConflictSeverity.HIGH,
                               "MEDIUM": ConflictSeverity.MEDIUM, "LOW": ConflictSeverity.LOW}
                new_conflict = Conflict(
                    conflict_type=conf.get('type'),
                    description=conf.get('description'),
                    severity=severity_map.get(conf.get('severity'), ConflictSeverity.MEDIUM),
                    project_id=project_id,
                    requirement_id_1=req1.id,
                    requirement_id_2=req2.id,
                    resolved=False
                )
                db.add(new_conflict)
                stored.append(new_conflict)
        db.commit()
        
        # Generate resolution suggestions for each stored conflict
        suggestions = {}
        for conf in stored:
            conflict_dict = {
                "type": conf.conflict_type,
                "details": {}
            }
            suggestions[conf.id] = ResolutionSuggester.suggest(conflict_dict)
        
        return {
            "project_id": project_id,
            "conflicts_detected": len(all_conflicts),
            "new_conflicts_stored": len(stored),
            "conflicts": [
                {
                    "id": c.id,
                    "type": c.conflict_type,
                    "description": c.description,
                    "severity": c.severity.value,
                    "suggestions": suggestions.get(c.id, [])
                } for c in stored
            ]
        }
    
    @classmethod
    def resolve_conflict(cls, conflict_id: int, resolution_text: str, db: Session) -> Dict:
        """Mark a conflict as resolved with the given resolution"""
        conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
        if not conflict:
            return {"error": "Conflict not found"}
        
        conflict.resolution = resolution_text
        conflict.resolved = True
        conflict.resolution_accepted = True
        db.commit()
        
        return {
            "conflict_id": conflict_id,
            "resolved": True,
            "resolution": resolution_text
        }
