"""Domain-specific parsing and coreference resolution"""
import re
from typing import Dict, Any, List, Optional

class ContextAnalyzer:
    """Understands domain-specific terms and resolves pronouns"""
    
    # Domain-specific term mappings
    DOMAIN_TERMS = {
        "ecommerce": {
            "cart": "shopping cart",
            "checkout": "order checkout process",
            "payment": "payment processing",
            "inventory": "product inventory management"
        },
        "healthcare": {
            "patient": "patient record",
            "doctor": "physician",
            "appointment": "medical appointment",
            "prescription": "medication prescription"
        },
        "finance": {
            "account": "financial account",
            "transaction": "financial transaction",
            "balance": "account balance",
            "fraud": "fraud detection"
        }
    }
    
    # Common pronoun mappings (will be resolved using previous context)
    PRONOUNS = ["it", "they", "them", "this", "that", "these", "those"]
    
    @classmethod
    def resolve_domain_terms(cls, text: str, domain: str) -> str:
        """Replace domain-specific abbreviations with full terms"""
        if domain not in cls.DOMAIN_TERMS:
            return text
        
        domain_map = cls.DOMAIN_TERMS[domain]
        text_lower = text.lower()
        for short, full in domain_map.items():
            # Replace whole word only
            pattern = r'\b' + re.escape(short) + r'\b'
            text = re.sub(pattern, full, text, flags=re.IGNORECASE)
        return text
    
    @classmethod
    def resolve_pronouns(cls, text: str, previous_entities: List[str]) -> str:
        """Replace pronouns with actual entities from context"""
        if not previous_entities:
            return text
        
        result = text
        # Simple heuristic: replace first pronoun with most recent entity
        for pronoun in cls.PRONOUNS:
            if pronoun in result.lower():
                # Replace the first occurrence
                result = re.sub(r'\b' + pronoun + r'\b', previous_entities[-1], result, count=1, flags=re.IGNORECASE)
        return result
    
    @classmethod
    def extract_implicit_requirements(cls, text: str, domain: str) -> List[str]:
        """Suggest implicit requirements based on domain patterns"""
        text_lower = text.lower()
        implicit = []
        
        # Domain-specific implicit requirements
        if domain == "ecommerce":
            if "payment" in text_lower:
                implicit.append("PCI-DSS compliance for payment processing")
                implicit.append("Secure storage of payment information")
            if "cart" in text_lower or "checkout" in text_lower:
                implicit.append("Abandoned cart recovery mechanism")
            if "inventory" in text_lower:
                implicit.append("Low stock alert system")
        
        elif domain == "healthcare":
            if "patient" in text_lower or "record" in text_lower:
                implicit.append("HIPAA compliance for patient data")
                implicit.append("Audit log for all data access")
        
        elif domain == "finance":
            if "transaction" in text_lower:
                implicit.append("ACID compliance for transactions")
                implicit.append("Fraud detection algorithms")
        
        return implicit
    
    @classmethod
    def analyze_context(cls, text: str, domain: str, previous_requirements: List[str] = None) -> Dict:
        """Full context analysis"""
        # Resolve domain terms
        expanded_text = cls.resolve_domain_terms(text, domain)
        
        # Resolve pronouns using previous requirement texts
        previous_entities = []
        if previous_requirements:
            # Extract nouns from previous requirements as potential entities
            for req in previous_requirements:
                words = re.findall(r'\b[A-Z][a-z]+\b', req)
                previous_entities.extend(words)
        resolved_text = cls.resolve_pronouns(expanded_text, previous_entities)
        
        # Extract implicit requirements
        implicit = cls.extract_implicit_requirements(resolved_text, domain)
        
        return {
            "original_text": text,
            "expanded_text": expanded_text,
            "resolved_text": resolved_text,
            "implicit_requirements": implicit,
            "domain": domain
        }
