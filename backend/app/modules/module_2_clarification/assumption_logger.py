"""Logs assumptions made during clarification process"""
from typing import List, Dict, Any
from datetime import datetime

class AssumptionLogger:
    """Tracks assumptions, inferences, and user confirmations"""
    
    def __init__(self):
        self.assumptions = []
    
    def log_assumption(self, original: str, clarified: str, confidence: float, source: str = "clarification"):
        """Log an assumption made by the system"""
        assumption = {
            "id": len(self.assumptions) + 1,
            "original": original,
            "clarified": clarified,
            "confidence": confidence,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "user_confirmed": False
        }
        self.assumptions.append(assumption)
        return assumption
    
    def confirm_assumption(self, assumption_id: int, confirmed: bool = True):
        """Mark an assumption as confirmed or rejected by user"""
        for assumption in self.assumptions:
            if assumption["id"] == assumption_id:
                assumption["user_confirmed"] = confirmed
                assumption["confirmed_at"] = datetime.utcnow().isoformat()
                return assumption
        return None
    
    def get_unconfirmed(self) -> List[Dict]:
        """Get all assumptions not yet confirmed by user"""
        return [a for a in self.assumptions if not a.get("user_confirmed")]
    
    def get_summary(self) -> Dict:
        """Get summary of all assumptions"""
        total = len(self.assumptions)
        confirmed = sum(1 for a in self.assumptions if a.get("user_confirmed") is True)
        rejected = sum(1 for a in self.assumptions if a.get("user_confirmed") is False)
        pending = total - confirmed - rejected
        
        return {
            "total_assumptions": total,
            "confirmed": confirmed,
            "rejected": rejected,
            "pending": pending,
            "assumptions": self.assumptions
        }
    
    def to_list(self) -> List[Dict]:
        """Return all assumptions as list"""
        return self.assumptions
    
    @classmethod
    def from_list(cls, assumptions_list: List[Dict]) -> "AssumptionLogger":
        """Recreate logger from stored assumptions"""
        logger = cls()
        logger.assumptions = assumptions_list
        return logger
