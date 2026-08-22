"""Automatically map requirements to regulatory compliance frameworks (GDPR, HIPAA, PCI-DSS)"""
from typing import Dict, Any, List

class ComplianceMapper:
    """Detect applicable regulations based on keywords"""
    
    REGULATIONS = {
        "GDPR": {
            "keywords": ["gdpr", "general data protection", "data protection", "privacy", "personal data", "european", "eu", "consent", "data subject", "right to be forgotten", "data portability"],
            "description": "EU General Data Protection Regulation",
            "priority_boost": "MUST"
        },
        "HIPAA": {
            "keywords": ["hipaa", "health insurance portability", "medical record", "patient data", "phi", "protected health information", "healthcare", "clinic", "hospital"],
            "description": "US Health Insurance Portability and Accountability Act",
            "priority_boost": "MUST"
        },
        "PCI-DSS": {
            "keywords": ["pci", "pci-dss", "payment card", "credit card", "debit card", "cardholder data", "cvv", "pan", "payment security", "card brand"],
            "description": "Payment Card Industry Data Security Standard",
            "priority_boost": "MUST"
        },
        "SOC2": {
            "keywords": ["soc2", "soc 2", "security controls", "availability", "confidentiality", "audit", "trust services"],
            "description": "Service Organization Control 2",
            "priority_boost": "SHOULD"
        },
        "CCPA": {
            "keywords": ["ccpa", "california consumer privacy", "california privacy", "consumer rights", "do not sell"],
            "description": "California Consumer Privacy Act",
            "priority_boost": "SHOULD"
        }
    }
    
    @classmethod
    def map_compliance(cls, text: str) -> Dict[str, Any]:
        """
        Returns list of applicable regulations and suggested priority boosts
        """
        text_lower = text.lower()
        applicable = []
        priority_boosts = []
        
        for reg, info in cls.REGULATIONS.items():
            matched_keywords = [kw for kw in info["keywords"] if kw in text_lower]
            if matched_keywords:
                applicable.append({
                    "regulation": reg,
                    "description": info["description"],
                    "matched_keywords": matched_keywords,
                    "confidence": min(0.95, 0.5 + len(matched_keywords) * 0.1),
                    "suggested_priority": info["priority_boost"]
                })
                priority_boosts.append(info["priority_boost"])
        
        return {
            "applicable_regulations": applicable,
            "has_compliance": len(applicable) > 0,
            "suggested_priority_boost": "MUST" if "MUST" in priority_boosts else ("SHOULD" if priority_boosts else None)
        }
    
    @classmethod
    def get_compliance_requirements(cls, regulation: str) -> List[str]:
        """Return standard requirement templates for a given regulation"""
        templates = {
            "GDPR": [
                "The system shall obtain explicit user consent before collecting personal data",
                "The system shall provide data export functionality in machine-readable format",
                "The system shall support the right to be forgotten (account deletion and data erasure)"
            ],
            "HIPAA": [
                "The system shall encrypt all protected health information (PHI) at rest and in transit",
                "The system shall maintain audit logs of all access to PHI for at least 6 years",
                "The system shall implement role-based access controls for PHI"
            ],
            "PCI-DSS": [
                "The system shall not store CVV or track data after authorization",
                "The system shall encrypt all cardholder data in transit using TLS 1.2+",
                "The system shall implement logging and monitoring for cardholder data environments"
            ]
        }
        return templates.get(regulation, [])
