"""Adjust priorities based on dependencies, compliance, and risk"""
from typing import List, Dict, Any

class PriorityAdjuster:
    """Refine MoSCoW priorities using additional context"""
    
    # Priority ordering: MUST > SHOULD > COULD > WONT
    PRIORITY_ORDER = {"MUST": 4, "SHOULD": 3, "COULD": 2, "WONT": 1}
    REVERSE_ORDER = {4: "MUST", 3: "SHOULD", 2: "COULD", 1: "WONT"}
    
    @classmethod
    def adjust_priority(cls, original_priority: str, dependencies: List[str], 
                       compliance_boost: str = None, risk_level: str = "LOW") -> Dict[str, Any]:
        """
        Adjust priority upward if dependencies are high or compliance mandates it.
        Returns adjusted priority and reasoning.
        """
        order = cls.PRIORITY_ORDER[original_priority]
        reasoning = []
        
        # Dependency chain length boost
        dep_count = len(dependencies)
        if dep_count > 3:
            order = min(4, order + 1)
            reasoning.append(f"High dependency count ({dep_count}) → priority increased")
        
        # Compliance boost (if compliance says MUST, and current is lower)
        if compliance_boost == "MUST" and order < 4:
            order = 4
            reasoning.append("Compliance requirement (GDPR/HIPAA/PCI) → priority raised to MUST")
        elif compliance_boost == "SHOULD" and order < 3:
            order = 3
            reasoning.append("Compliance recommendation → priority raised to SHOULD")
        
        # Risk boost
        if risk_level == "HIGH" and order < 4:
            order = min(4, order + 1)
            reasoning.append("High risk → priority increased")
        
        adjusted_priority = cls.REVERSE_ORDER[order]
        
        return {
            "original_priority": original_priority,
            "adjusted_priority": adjusted_priority,
            "changed": original_priority != adjusted_priority,
            "reasoning": reasoning if reasoning else ["No adjustment needed"]
        }
    
    @classmethod
    def batch_adjust(cls, requirements_metadata: List[Dict]) -> List[Dict]:
        """Adjust multiple requirements"""
        results = []
        for req in requirements_metadata:
            adjustment = cls.adjust_priority(
                original_priority=req.get("priority", "SHOULD"),
                dependencies=req.get("dependencies", []),
                compliance_boost=req.get("compliance_boost"),
                risk_level=req.get("risk_level", "LOW")
            )
            results.append({
                "requirement_id": req.get("requirement_id"),
                "original": adjustment["original_priority"],
                "adjusted": adjustment["adjusted_priority"],
                "changed": adjustment["changed"],
                "reasoning": adjustment["reasoning"]
            })
        return results
