"""Service to run full impact analysis on a project"""
from backend.app.modules.module_7_impact_analyzer import (
    ComplexityScorer, EffortEstimator, DependencyMapper, RiskAssessor
)
from backend.app.database.models import Requirement, Project
from sqlalchemy.orm import Session
from typing import Dict, List

class ImpactAnalysisService:
    @classmethod
    def analyze_project(cls, project_id: int, db: Session) -> Dict:
        """Run all impact analyses and update requirement fields in DB"""
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        if not requirements:
            return {"message": "No requirements found", "project_id": project_id}
        
        req_list = [
            {
                "id": r.id,
                "requirement_id": r.requirement_id,
                "text": r.text,
                "category": r.category
            }
            for r in requirements
        ]
        
        # 1. Complexity scoring
        complexity_results = ComplexityScorer.batch_score(req_list)
        # Map back to requirement objects
        complexity_map = {res["requirement_id"]: res["complexity"] for res in complexity_results}
        
        # 2. Effort estimation
        effort_results = []
        for res in complexity_results:
            req_id = res["requirement_id"]
            complexity = res["complexity"]["score"]
            # find category
            category = next((r["category"] for r in req_list if r["requirement_id"] == req_id), "General")
            effort = EffortEstimator.estimate(complexity, category)
            effort_results.append({"requirement_id": req_id, "effort": effort})
        effort_map = {res["requirement_id"]: res["effort"] for res in effort_results}
        
        # 3. Dependency mapping
        dependency_result = DependencyMapper.build_dependency_graph(req_list)
        # Store dependencies as JSON in project metadata? For now, just compute
        dependency_list = {}
        for rid, deps in dependency_result["graph"].items():
            dependency_list[rid] = deps
        
        # 4. Risk assessment
        risk_results = []
        for req in req_list:
            rid = req["requirement_id"]
            complexity = complexity_map[rid]["score"]
            effort_hours = effort_map[rid]["hours"]
            deps = dependency_list.get(rid, [])
            risk = RiskAssessor.assess(complexity, effort_hours, len(deps))
            risk_results.append({"requirement_id": rid, "risk": risk})
        risk_map = {res["requirement_id"]: res["risk"] for res in risk_results}
        
        # 5. Update database with impact metrics (complexity, effort, risk)
        for r in requirements:
            rid = r.requirement_id
            r.complexity = complexity_map.get(rid, {}).get("score", 1)
            r.effort_hours = effort_map.get(rid, {}).get("hours", 0.0)
            r.quality_score = int(10 - risk_map.get(rid, {}).get("risk_score", 5))  # simple inverse risk
        db.commit()
        
        # Prepare response
        full_results = []
        for req in req_list:
            rid = req["requirement_id"]
            full_results.append({
                "requirement_id": rid,
                "text": req["text"][:100],
                "complexity": complexity_map[rid],
                "effort": effort_map[rid],
                "dependencies": dependency_list.get(rid, []),
                "risk": risk_map[rid]
            })
        
        # Compute project totals
        total_effort = sum(e["effort"]["hours"] for e in effort_results)
        max_complexity = max((c["complexity"]["score"] for c in complexity_results), default=0)
        high_risks = sum(1 for r in risk_results if r["risk"]["level"] == "HIGH")
        
        return {
            "project_id": project_id,
            "requirements_analyzed": len(requirements),
            "total_effort_hours": round(total_effort, 1),
            "total_person_days": round(total_effort / 8, 1),
            "total_person_weeks": round(total_effort / 40, 1),
            "max_complexity": max_complexity,
            "high_risk_count": high_risks,
            "critical_path": dependency_result["critical_path"],
            "details": full_results
        }
