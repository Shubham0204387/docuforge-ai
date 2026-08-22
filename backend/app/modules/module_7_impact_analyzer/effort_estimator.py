"""Estimate effort in person-hours based on complexity and historical data"""
from typing import Dict, Any, List

class EffortEstimator:
    """Convert complexity score to effort hours using industry baselines"""
    
    # Base hours per complexity point (calibrated for a typical developer)
    # Derived from COCOMO and functional point analysis approximations
    BASE_HOURS_PER_POINT = 5.5   # 1 complexity point ~ 5.5 hours
    
    # Multipliers for different categories (can be adjusted)
    CATEGORY_MULTIPLIER = {
        "User Management": 1.0,
        "Order Management": 1.2,
        "Payment": 1.5,      # PCI, gateway integration
        "Security": 1.8,
        "Notifications": 0.8,
        "Reporting": 1.0,
        "Integration": 1.6,
        "Infrastructure": 1.3,
        "Location Services": 1.4,
        "General": 1.0
    }
    
    @classmethod
    def estimate(cls, complexity_score: int, category: str = None, additional_factors: Dict = None) -> Dict[str, Any]:
        """
        Estimate effort in person-hours
        Returns: {"hours": float, "person_days": float, "person_weeks": float, "confidence": str}
        """
        base_hours = complexity_score * cls.BASE_HOURS_PER_POINT
        
        # Apply category multiplier
        multiplier = cls.CATEGORY_MULTIPLIER.get(category, 1.0)
        adjusted_hours = base_hours * multiplier
        
        # Additional factors (e.g., team size, experience - can be extended)
        if additional_factors:
            if additional_factors.get("junior_developer"):
                adjusted_hours *= 1.3
            if additional_factors.get("tight_deadline"):
                adjusted_hours *= 1.2
        
        hours = round(adjusted_hours, 1)
        person_days = round(hours / 8, 1)
        person_weeks = round(person_days / 5, 1)
        
        # Confidence based on category specificity
        confidence = "MEDIUM"
        if category and category != "General":
            confidence = "HIGH"
        elif complexity_score > 8:
            confidence = "LOW"
        
        return {
            "hours": hours,
            "person_days": person_days,
            "person_weeks": person_weeks,
            "confidence": confidence,
            "calculation": {
                "base_hours": base_hours,
                "multiplier": multiplier,
                "complexity_score": complexity_score
            }
        }
    
    @classmethod
    def batch_estimate(cls, requirements_with_complexity: List[Dict]) -> List[Dict]:
        """Estimate effort for multiple requirements"""
        results = []
        for req in requirements_with_complexity:
            complexity = req.get('complexity', {}).get('score', 5)
            category = req.get('category')
            effort = cls.estimate(complexity, category)
            results.append({
                "requirement_id": req.get('requirement_id'),
                "effort": effort
            })
        return results
