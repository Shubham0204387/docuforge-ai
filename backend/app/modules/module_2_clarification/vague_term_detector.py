"""Detects vague or subjective terms in requirements"""
import re
from typing import List, Dict, Any, Set

class VagueTermDetector:
    """Identifies ambiguous language that needs clarification"""
    
    # Vague terms categorized by type
    VAGUE_TERMS = {
        "performance": [
            "fast", "slow", "quick", "rapid", "speedy", "efficient",
            "high performance", "low latency", "responsive"
        ],
        "quality": [
            "good", "bad", "excellent", "poor", "high quality", "reliable",
            "robust", "stable", "user-friendly", "intuitive", "easy to use"
        ],
        "quantity": [
            "many", "few", "several", "numerous", "countless", "lot of",
            "a lot", "plenty", "handful", "bunch of"
        ],
        "security": [
            "secure", "safe", "protected", "encrypted", "authorized",
            "authenticated", "private", "confidential"
        ],
        "scalability": [
            "scalable", "grow", "expand", "handle growth", "large scale",
            "high volume", "millions of users"
        ],
        "time": [
            "real-time", "instant", "immediate", "soon", "quickly",
            "asap", "within seconds", "near real-time"
        ],
        "frequency": [
            "often", "frequently", "regularly", "periodically", "occasionally",
            "rarely", "sometimes", "constantly"
        ],
        "size": [
            "large", "small", "huge", "tiny", "big", "little", "massive",
            "moderate", "average"
        ]
    }
    
    # Domain-specific vague patterns
    DOMAIN_PATTERNS = {
        "ecommerce": ["affordable", "competitive pricing", "wide selection"],
        "healthcare": ["accurate", "compliant", "safe", "confidential"],
        "finance": ["low risk", "high return", "fraud-proof"],
        "education": ["engaging", "interactive", "effective"],
        "gaming": ["immersive", "addictive", "smooth gameplay"]
    }
    
    @classmethod
    def detect(cls, text: str, domain: str = "general") -> Dict[str, Any]:
        """
        Detect vague terms in text
        Returns: {
            "has_vague": bool,
            "vague_terms": list,
            "categories": dict,
            "suggestions": list
        }
        """
        text_lower = text.lower()
        detected = []
        categories = {cat: [] for cat in cls.VAGUE_TERMS.keys()}
        
        # Check standard vague terms
        for category, terms in cls.VAGUE_TERMS.items():
            for term in terms:
                if term in text_lower:
                    detected.append(term)
                    categories[category].append(term)
        
        # Check domain-specific patterns
        domain_patterns = cls.DOMAIN_PATTERNS.get(domain, [])
        for pattern in domain_patterns:
            if pattern in text_lower:
                detected.append(pattern)
                categories["domain_specific"] = categories.get("domain_specific", []) + [pattern]
        
        # Generate suggestions for each detected vague term
        suggestions = []
        for term in set(detected):
            suggestion = cls._get_suggestion(term, domain)
            suggestions.append({"term": term, "suggestion": suggestion})
        
        return {
            "has_vague": len(detected) > 0,
            "vague_terms": list(set(detected)),
            "categories": categories,
            "suggestions": suggestions,
            "count": len(set(detected))
        }
    
    @classmethod
    def _get_suggestion(cls, term: str, domain: str) -> str:
        """Generate a clarification suggestion for a vague term"""
        suggestions_map = {
            "fast": "Define 'fast' as a specific response time (e.g., < 2 seconds, < 100ms)",
            "real-time": "Specify update frequency (e.g., every 30 seconds, every 1 second, continuous)",
            "secure": "Specify security standards (e.g., TLS 1.3, AES-256, OAuth2, SOC2 compliance)",
            "scalable": "Specify expected user/transaction volume (e.g., 1000 concurrent users, 10k requests/sec)",
            "user-friendly": "Describe specific UX requirements (e.g., < 3 clicks to complete task, mobile-optimized)",
            "good": "Replace 'good' with measurable quality criteria (e.g., 99.9% uptime, < 1% error rate)",
            "many": "Provide an approximate number or range (e.g., 100-500 items, up to 10,000 users)",
            "affordable": "Specify price range or budget constraint (e.g., $10-20 per month, under $50K total)",
            "efficient": "Define efficiency metrics (e.g., CPU usage < 30%, response time < 500ms)",
        }
        
        if term in suggestions_map:
            return suggestions_map[term]
        return f"Clarify '{term}' with specific, measurable criteria"
