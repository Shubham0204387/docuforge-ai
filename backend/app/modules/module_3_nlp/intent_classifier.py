"""Classify requirement intent: functional, non-functional, or constraint"""
import re
from typing import Dict, Any, List

class IntentClassifier:
    """Classifies the type of requirement based on language patterns"""
    
    # Keywords indicating functional requirements
    FUNCTIONAL_KEYWORDS = [
        "shall", "will", "must", "should", "can", "may", "able to",
        "allow", "enable", "provide", "support", "perform", "execute"
    ]
    
    # Keywords indicating non-functional requirements
    NONFUNCTIONAL_KEYWORDS = {
        "performance": ["response time", "latency", "throughput", "speed", "fast", "slow", "efficient"],
        "security": ["secure", "encrypt", "authenticate", "authorize", "privacy", "confidential", "integrity"],
        "usability": ["user-friendly", "intuitive", "easy to use", "accessible", "responsive"],
        "reliability": ["uptime", "available", "fault-tolerant", "recover", "backup", "disaster"],
        "scalability": ["scale", "concurrent", "load", "traffic", "grow", "expand"],
        "maintainability": ["modular", "documented", "testable", "extensible", "configurable"]
    }
    
    # Keywords indicating constraints
    CONSTRAINT_KEYWORDS = [
        "must comply", "must adhere", "required by", "regulated by",
        "limited to", "restricted", "cannot", "may not", "prohibited",
        "budget", "timeline", "deadline", "platform", "technology"
    ]
    
    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Classify requirement as functional, non-functional, or constraint
        Returns: {
            "type": str,
            "subtype": str (for non-functional),
            "confidence": float,
            "matched_keywords": list
        }
        """
        text_lower = text.lower()
        
        # Check for constraint first (highest priority)
        for keyword in cls.CONSTRAINT_KEYWORDS:
            if keyword in text_lower:
                return {
                    "type": "constraint",
                    "subtype": None,
                    "confidence": 0.85,
                    "matched_keywords": [keyword]
                }
        
        # Check for non-functional
        for nf_type, keywords in cls.NONFUNCTIONAL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {
                        "type": "non_functional",
                        "subtype": nf_type,
                        "confidence": 0.8,
                        "matched_keywords": [keyword]
                    }
        
        # Check for functional
        for keyword in cls.FUNCTIONAL_KEYWORDS:
            if keyword in text_lower:
                return {
                    "type": "functional",
                    "subtype": None,
                    "confidence": 0.9,
                    "matched_keywords": [keyword]
                }
        
        # Default to functional with lower confidence
        return {
            "type": "functional",
            "subtype": None,
            "confidence": 0.6,
            "matched_keywords": []
        }
    
    @classmethod
    def batch_classify(cls, requirements: List[Dict]) -> List[Dict]:
        """Classify multiple requirements"""
        results = []
        for req in requirements:
            text = req.get("text", "")
            classification = cls.classify(text)
            results.append({
                "requirement_id": req.get("id", req.get("requirement_id")),
                "text": text[:100],
                "classification": classification
            })
        return results
