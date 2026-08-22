"""Estimate business value (0-100) based on factors like revenue, customer impact, competitive advantage"""
from typing import Dict, Any

class BusinessValueCalculator:
    """Calculate business value score using heuristic rules"""
    
    @classmethod
    def calculate(cls, text: str, complexity_score: int = 5, category: str = None) -> Dict[str, Any]:
        """
        Returns business value score (0-100) and breakdown
        """
        text_lower = text.lower()
        score = 50  # base
        factors = {}
        
        # Revenue impact keywords
        revenue_keywords = ["payment", "checkout", "transaction", "sell", "purchase", "subscription", "premium"]
        revenue_count = sum(1 for kw in revenue_keywords if kw in text_lower)
        revenue_bonus = min(30, revenue_count * 10)
        score += revenue_bonus
        factors["revenue_potential"] = revenue_bonus
        
        # Customer satisfaction / retention
        retention_keywords = ["user experience", "retention", "satisfaction", "feedback", "rating", "review"]
        retention_count = sum(1 for kw in retention_keywords if kw in text_lower)
        retention_bonus = min(20, retention_count * 10)
        score += retention_bonus
        factors["customer_impact"] = retention_bonus
        
        # Competitive advantage
        competitive_keywords = ["differentiator", "unique", "advantage", "competitor", "market", "leading"]
        competitive_count = sum(1 for kw in competitive_keywords if kw in text_lower)
        competitive_bonus = min(20, competitive_count * 10)
        score += competitive_bonus
        factors["competitive_advantage"] = competitive_bonus
        
        # Compliance/risk reduction (avoid penalties)
        compliance_keywords = ["compliance", "gdpr", "hipaa", "pci", "audit", "legal", "regulation"]
        compliance_count = sum(1 for kw in compliance_keywords if kw in text_lower)
        compliance_bonus = min(20, compliance_count * 10)
        score += compliance_bonus
        factors["risk_mitigation"] = compliance_bonus
        
        # Category boosts
        if category:
            category_boosts = {
                "Payment": 15,
                "Security": 15,
                "User Management": 10,
                "Order Management": 10,
                "Compliance": 20,
                "Reporting": 5
            }
            boost = category_boosts.get(category, 0)
            score += boost
            factors["category_boost"] = boost
        
        # Cap at 100
        score = min(100, score)
        
        # Determine level
        if score >= 80:
            level = "HIGH"
        elif score >= 50:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        # Estimate ROI factor (simplified: value / (effort/complexity))
        roi_factor = round(score / max(1, complexity_score), 1)
        
        return {
            "score": score,
            "level": level,
            "factors": factors,
            "roi_factor": roi_factor,
            "summary": f"Business Value: {score}/100 ({level})"
        }
