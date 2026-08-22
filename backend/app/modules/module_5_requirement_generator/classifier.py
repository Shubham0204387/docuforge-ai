"""Classify requirements by priority, category, and testability"""
from typing import Dict, Any, List
import re

class Classifier:
    """Determines priority, category, and testability score for a requirement"""
    
    # Priority keywords with weights
    PRIORITY_KEYWORDS = {
        "MUST": {
            "keywords": ["must", "critical", "essential", "required", "mandatory", "shall"],
            "weight": 10
        },
        "SHOULD": {
            "keywords": ["should", "important", "recommended", "desirable"],
            "weight": 7
        },
        "COULD": {
            "keywords": ["could", "may", "optional", "nice to have", "if possible"],
            "weight": 4
        },
        "WONT": {
            "keywords": ["won't", "will not", "not required", "out of scope"],
            "weight": 1
        }
    }
    
    # Category detection
    CATEGORY_KEYWORDS = {
        "User Management": ["user", "account", "profile", "login", "register", "authentication"],
        "Order Management": ["order", "cart", "checkout", "purchase", "transaction"],
        "Payment": ["payment", "pay", "credit card", "debit", "invoice", "refund"],
        "Security": ["security", "encrypt", "pci", "gdpr", "privacy", "compliance"],
        "Performance": ["performance", "response time", "latency", "throughput", "speed"],
        "Notifications": ["notify", "alert", "push", "email", "sms", "message"],
        "Reporting": ["report", "analytics", "dashboard", "statistics", "insight"],
        "Integration": ["api", "integration", "webhook", "third-party", "external"],
        "Infrastructure": ["deploy", "scale", "backup", "monitor", "log", "audit"],
        "Location Services": ["location", "gps", "map", "tracking", "geolocation"]
    }
    
    # Testability scoring (0-100)
    TESTABILITY_RULES = [
        (r'\d+ seconds?|\d+ ms|\d+ minutes?', 20),  # Measurable time
        (r'\d+%|percentage', 15),                    # Percentage metric
        (r'\d+ users?|\d+ concurrent', 15),          # User count
        (r'\b(shall|must|will)\b', 10),              # Clear requirement language
        (r'\b(validate|verify|check|ensure)\b', 10), # Verification action
        (r'\b(response|result|output)\b', 10),       # Observable outcome
        (r'\b(if|when|while)\b', 5),                 # Condition present
    ]
    
    @classmethod
    def classify_priority(cls, text: str) -> Dict[str, Any]:
        """Determine priority based on keyword matching"""
        text_lower = text.lower()
        scores = {}
        
        for priority, config in cls.PRIORITY_KEYWORDS.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += config["weight"]
            scores[priority] = score
        
        # Find highest scoring priority
        best_priority = max(scores, key=scores.get)
        confidence = min(0.95, scores[best_priority] / 20)
        
        return {
            "priority": best_priority,
            "confidence": round(confidence, 2),
            "scores": scores
        }
    
    @classmethod
    def classify_category(cls, text: str) -> str:
        """Determine the most relevant category"""
        text_lower = text.lower()
        best_category = "General"
        best_score = 0
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    @classmethod
    def calculate_testability(cls, text: str) -> Dict[str, Any]:
        """Calculate testability score (0-100)"""
        text_lower = text.lower()
        score = 0
        matched_rules = []
        
        for pattern, points in cls.TESTABILITY_RULES:
            if re.search(pattern, text_lower):
                score += points
                matched_rules.append(pattern)
        
        # Cap at 100
        score = min(100, score)
        
        # Determine testability level
        if score >= 70:
            level = "HIGH"
        elif score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return {
            "score": score,
            "level": level,
            "matched_rules": matched_rules,
            "suggestion": "Add measurable criteria" if score < 50 else "Testable"
        }
    
    @classmethod
    def classify_full(cls, text: str, req_type: str = "functional") -> Dict[str, Any]:
        """Perform all classifications"""
        priority = cls.classify_priority(text)
        category = cls.classify_category(text)
        testability = cls.calculate_testability(text)
        
        return {
            "requirement_text": text,
            "type": req_type,
            "priority": priority["priority"],
            "priority_confidence": priority["confidence"],
            "category": category,
            "testability_score": testability["score"],
            "testability_level": testability["level"],
            "testability_suggestion": testability["suggestion"]
        }
