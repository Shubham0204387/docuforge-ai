"""Calculate Requirement Quality Index (RQI) as weighted average"""
from typing import Dict, Any

class RQICalculator:
    @classmethod
    def calculate(cls, smart_result: Dict, ambiguity_result: Dict, completeness_result: Dict) -> Dict[str, Any]:
        smart_score = smart_result.get('overall', 0)
        clarity_score = ambiguity_result.get('clarity_score', 0)
        completeness_score = completeness_result.get('completeness_score', 0)
        weights = {"smart": 0.35, "clarity": 0.30, "completeness": 0.35}
        rqi = smart_score * weights["smart"] + clarity_score * weights["clarity"] + completeness_score * weights["completeness"]
        rqi = round(rqi, 1)
        rating = "Excellent" if rqi >= 85 else "Good" if rqi >= 70 else "Fair" if rqi >= 50 else "Poor"
        return {
            "rqi_score": rqi,
            "rating": rating,
            "components": {"smart": smart_score, "clarity": clarity_score, "completeness": completeness_score},
            "summary": f"RQI: {rqi} ({rating})"
        }
