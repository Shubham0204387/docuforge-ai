"""MoSCoW classification with confidence scoring based on keywords and heuristics"""
import re
from typing import Dict, Any, List

class MoSCoWClassifier:
    """Classify requirement priority as Must, Should, Could, or Won't"""
    
    # Keywords with weights for each category
    KEYWORDS = {
        "MUST": {
            "words": ["must", "critical", "essential", "required", "mandatory", "shall", "necessary", "fundamental"],
            "weight": 10
        },
        "SHOULD": {
            "words": ["should", "important", "recommended", "desirable", "preferable", "valuable"],
            "weight": 7
        },
        "COULD": {
            "words": ["could", "may", "optional", "nice to have", "if possible", "eventually", "maybe"],
            "weight": 4
        },
        "WONT": {
            "words": ["won't", "will not", "not required", "out of scope", "excluded", "no need"],
            "weight": 1
        }
    }
    
    # Domain-specific adjustments (e.g., security requirements often MUST)
    DOMAIN_BOOST = {
        "ecommerce": {"payment": "MUST", "security": "MUST", "inventory": "SHOULD"},
        "healthcare": {"patient": "MUST", "compliance": "MUST", "reporting": "SHOULD"},
        "finance": {"transaction": "MUST", "audit": "MUST", "reporting": "SHOULD"},
        "general": {}
    }
    
    @classmethod
    def classify(cls, text: str, domain: str = "general", category: str = None) -> Dict[str, Any]:
        """
        Return MoSCoW classification with confidence score
        Returns: {"priority": str, "confidence": float, "scores": dict, "reasoning": str}
        """
        text_lower = text.lower()
        scores = {cat: 0 for cat in cls.KEYWORDS}
        
        # Score based on keywords
        for cat, config in cls.KEYWORDS.items():
            for word in config["words"]:
                if word in text_lower:
                    scores[cat] += config["weight"]
        
        # Domain-specific boost
        if domain in cls.DOMAIN_BOOST:
            domain_map = cls.DOMAIN_BOOST[domain]
            for key, boost_cat in domain_map.items():
                if key in text_lower:
                    scores[boost_cat] += 5
        
        # Category-based boost (e.g., Security -> MUST)
        if category:
            if category.lower() in ["security", "payment", "compliance"]:
                scores["MUST"] += 8
        
        # Find highest scoring category
        max_cat = max(scores, key=scores.get)
        max_score = scores[max_cat]
        total_score = sum(scores.values())
        confidence = min(0.95, max_score / 20 if total_score > 0 else 0.5)
        
        # Special handling: if no keywords matched, default to SHOULD
        if total_score == 0:
            max_cat = "SHOULD"
            confidence = 0.5
        
        # Generate reasoning
        reasoning = f"Matched keywords: {[w for w in cls.KEYWORDS[max_cat]['words'] if w in text_lower]}"
        if not reasoning:
            reasoning = "No strong indicators, defaulted to SHOULD"
        
        return {
            "priority": max_cat,
            "confidence": round(confidence, 2),
            "scores": scores,
            "reasoning": reasoning
        }
