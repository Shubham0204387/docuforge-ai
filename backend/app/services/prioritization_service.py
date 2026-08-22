"""Service to apply all prioritization and compliance logic to a project"""
from backend.app.modules.module_9_prioritizer import (
    MoSCoWClassifier, BusinessValueCalculator, ComplianceMapper, PriorityAdjuster
)
from backend.app.database.models import Requirement, Project, Priority
from sqlalchemy.orm import Session
from typing import Dict, List

class PrioritizationService:
    @classmethod
    def prioritize_project(cls, project_id: int, db: Session) -> Dict:
        """Run all prioritization analyses on project requirements and update DB"""
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        if not requirements:
            return {"message": "No requirements found", "project_id": project_id}
        
        # Get project domain
        project = db.query(Project).filter(Project.id == project_id).first()
        domain = project.domain if project else "general"
        
        results = []
        for req in requirements:
            # 1. MoSCoW classification
            moscow = MoSCoWClassifier.classify(req.text, domain, req.category)
            
            # 2. Business value calculation
            business_value = BusinessValueCalculator.calculate(
                req.text, 
                req.complexity or 5,
                req.category
            )
            
            # 3. Compliance mapping
            compliance = ComplianceMapper.map_compliance(req.text)
            
            # 4. Priority adjustment (using dependencies from impact module)
            # For now, use placeholder dependencies; later we can fetch from graph
            dependencies = []  # could be fetched from DependencyMapper if available
            
            risk_level = "LOW"
            if req.complexity and req.complexity > 7:
                risk_level = "HIGH"
            elif req.complexity and req.complexity > 4:
                risk_level = "MEDIUM"
            
            compliance_boost = None
            if compliance.get("suggested_priority_boost"):
                compliance_boost = compliance["suggested_priority_boost"]
            
            adjustment = PriorityAdjuster.adjust_priority(
                original_priority=moscow["priority"],
                dependencies=dependencies,
                compliance_boost=compliance_boost,
                risk_level=risk_level
            )
            
            # Update requirement in database
            priority_map = {"MUST": Priority.MUST, "SHOULD": Priority.SHOULD,
                           "COULD": Priority.COULD, "WONT": Priority.WONT}
            req.priority = priority_map.get(adjustment["adjusted_priority"], Priority.SHOULD)
            req.priority_confidence = moscow["confidence"]
            req.business_value = business_value["score"]
            
            results.append({
                "requirement_id": req.requirement_id,
                "text": req.text[:100],
                "moscow": moscow,
                "business_value": business_value,
                "compliance": compliance,
                "adjusted_priority": adjustment["adjusted_priority"],
                "priority_changed": adjustment["changed"],
                "adjustment_reasoning": adjustment["reasoning"]
            })
        
        db.commit()
        
        # Summary statistics
        priority_counts = {"MUST": 0, "SHOULD": 0, "COULD": 0, "WONT": 0}
        for r in results:
            p = r["adjusted_priority"]
            priority_counts[p] += 1
        
        return {
            "project_id": project.project_id,
            "requirements_processed": len(requirements),
            "priority_distribution": priority_counts,
            "average_business_value": round(sum(r["business_value"]["score"] for r in results) / len(results), 1),
            "details": results
        }
    
    @classmethod
    def prioritize_single_requirement(cls, text: str, domain: str = "general", 
                                     complexity: int = 5, category: str = None) -> Dict:
        """Prioritize a single requirement text without DB update"""
        moscow = MoSCoWClassifier.classify(text, domain, category)
        business_value = BusinessValueCalculator.calculate(text, complexity, category)
        compliance = ComplianceMapper.map_compliance(text)
        
        compliance_boost = compliance.get("suggested_priority_boost")
        adjustment = PriorityAdjuster.adjust_priority(
            original_priority=moscow["priority"],
            dependencies=[],
            compliance_boost=compliance_boost,
            risk_level="MEDIUM" if complexity > 5 else "LOW"
        )
        
        return {
            "original_text": text,
            "moscow": moscow,
            "business_value": business_value,
            "compliance": compliance,
            "adjusted_priority": adjustment["adjusted_priority"],
            "final_priority": adjustment["adjusted_priority"],
            "reasoning": adjustment["reasoning"]
        }
