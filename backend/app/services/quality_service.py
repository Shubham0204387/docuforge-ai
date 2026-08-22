"""Service to run quality assessment on requirements"""
from backend.app.modules.module_8_quality_assessor import (
    SMARTCriteriaChecker, AmbiguityDetector, CompletenessValidator, RQICalculator
)
from backend.app.database.models import Requirement, Project
from sqlalchemy.orm import Session
from typing import Dict

class QualityAssessmentService:
    @classmethod
    def assess_requirement(cls, text: str) -> Dict:
        smart = SMARTCriteriaChecker.check(text)
        ambiguity = AmbiguityDetector.detect(text)
        completeness = CompletenessValidator.validate(text)
        rqi = RQICalculator.calculate(smart, ambiguity, completeness)
        return {"smart": smart, "ambiguity": ambiguity, "completeness": completeness, "rqi": rqi}
    
    @classmethod
    def assess_project(cls, project_id: int, db: Session) -> Dict:
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        if not requirements:
            return {"message": "No requirements found", "project_id": project_id}
        results = []
        total_rqi = 0
        for req in requirements:
            assessment = cls.assess_requirement(req.text)
            rqi_score = assessment["rqi"]["rqi_score"]
            total_rqi += rqi_score
            req.quality_score = rqi_score
            results.append({
                "requirement_id": req.requirement_id,
                "text": req.text[:100],
                "rqi_score": rqi_score,
                "rating": assessment["rqi"]["rating"],
                "details": assessment
            })
        db.commit()
        avg_rqi = round(total_rqi / len(requirements), 1) if requirements else 0
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        for r in results:
            rating = r["rating"]
            if rating == "Excellent": distribution["excellent"] += 1
            elif rating == "Good": distribution["good"] += 1
            elif rating == "Fair": distribution["fair"] += 1
            else: distribution["poor"] += 1
        return {
            "project_id": project_id,
            "requirements_assessed": len(requirements),
            "average_rqi": avg_rqi,
            "distribution": distribution,
            "details": results
        }
