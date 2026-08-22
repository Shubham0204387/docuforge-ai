"""Classify domain from input text"""
import re
from typing import Dict, Any, List, Tuple

class DomainClassifier:
    """Classifies project domain based on keywords"""
    
    DOMAINS = {
        "ecommerce": {
            "keywords": ["shop", "store", "buy", "sell", "cart", "checkout", "payment", "product", "inventory", "order", "delivery", "shipping"],
            "weight": 2
        },
        "healthcare": {
            "keywords": ["patient", "doctor", "clinic", "hospital", "medical", "health", "appointment", "prescription", "diagnosis", "treatment", "record", "hipaa"],
            "weight": 3
        },
        "finance": {
            "keywords": ["bank", "account", "transaction", "payment", "loan", "credit", "debit", "investment", "stock", "trading", "pci", "fraud"],
            "weight": 3
        },
        "education": {
            "keywords": ["student", "teacher", "course", "class", "assignment", "grade", "exam", "quiz", "learning", "training", "curriculum"],
            "weight": 2
        },
        "gaming": {
            "keywords": ["game", "player", "level", "score", "multiplayer", "character", "quest", "achievement", "leaderboard", "tournament"],
            "weight": 2
        },
        "social_media": {
            "keywords": ["post", "share", "like", "comment", "follow", "friend", "message", "feed", "profile", "timeline", "notification"],
            "weight": 2
        },
        "productivity": {
            "keywords": ["task", "project", "deadline", "team", "collaboration", "workspace", "document", "file", "calendar", "schedule", "reminder"],
            "weight": 1
        }
    }
    
    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Classify domain from text
        Returns: {domain: str, confidence: float, alternatives: list}
        """
        text_lower = text.lower()
        scores = {}
        
        for domain, config in cls.DOMAINS.items():
            score = 0
            matched_keywords = []
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += config["weight"]
                    matched_keywords.append(keyword)
            if score > 0:
                scores[domain] = {"score": score, "matched_keywords": matched_keywords}
        
        if not scores:
            return {
                "domain": "general",
                "confidence": 0.5,
                "alternatives": [],
                "matched_keywords": []
            }
        
        # Sort by score
        sorted_domains = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        top_domain = sorted_domains[0]
        
        # Calculate confidence (0-1)
        max_possible_score = sum([c["weight"] for c in cls.DOMAINS.values()])
        confidence = min(0.95, top_domain[1]["score"] / 10)
        
        return {
            "domain": top_domain[0],
            "confidence": round(confidence, 2),
            "alternatives": [d for d, _ in sorted_domains[1:3]],
            "matched_keywords": top_domain[1]["matched_keywords"]
        }
