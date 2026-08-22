"""Calculate risk scores based on complexity, effort, and dependencies"""
from typing import Dict, Any, List

class RiskAssessor:
    """Compute probability, impact, and overall risk score for each requirement"""
    
    @classmethod
    def assess(cls, complexity_score: int, effort_hours: float, dependency_count: int) -> Dict[str, Any]:
        """
        Risk = Probability × Impact (both scaled 0-1)
        Returns: {"probability": float, "impact": float, "risk_score": float, "level": str}
        """
        # Probability factors: complexity (0-1 scaled), dependency count (capped)
        prob_complexity = min(1.0, complexity_score / 10)
        prob_dependency = min(0.5, dependency_count / 10)  # dependencies increase probability
        probability = round((prob_complexity + prob_dependency) / 1.5, 2)
        
        # Impact factors: effort (hours -> 0-1 scale, 100 hours = 1.0)
        impact_effort = min(1.0, effort_hours / 100)
        impact = round(impact_effort, 2)
        
        risk_score = round(probability * impact * 10, 1)  # 0-10 scale
        if risk_score >= 7:
            level = "HIGH"
        elif risk_score >= 4:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return {
            "probability": probability,
            "impact": impact,
            "risk_score": risk_score,
            "level": level,
            "matrix_position": f"({probability},{impact})"
        }
    
    @classmethod
    def batch_assess(cls, requirements_metrics: List[Dict]) -> List[Dict]:
        """Assess risk for multiple requirements"""
        results = []
        for req in requirements_metrics:
            risk = cls.assess(
                req.get('complexity', {}).get('score', 5),
                req.get('effort', {}).get('hours', 0),
                len(req.get('dependencies', []))
            )
            results.append({
                "requirement_id": req.get('requirement_id'),
                "risk": risk
            })
        return results
