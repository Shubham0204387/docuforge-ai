"""Apply inference rules to expand requirements"""
from typing import List, Dict, Any, Set
from backend.app.modules.module_4_knowledge_graph.pattern_matcher import PatternMatcher

class InferenceEngine:
    """Applies if-then rules to generate new requirements"""
    
    @classmethod
    def apply_rules(cls, text: str, rules: List[Dict]) -> List[Dict]:
        """
        Apply all inference rules to input text
        Returns list of generated requirements with confidence scores
        """
        text_lower = text.lower()
        generated = []
        used_rules = set()
        
        for rule in rules:
            # Get trigger keywords
            if_contains = rule.get('if_contains', [])
            matched_keywords = PatternMatcher.match_keywords(text_lower, if_contains)
            
            if matched_keywords:
                rule_id = rule.get('id')
                if rule_id in used_rules:
                    continue
                used_rules.add(rule_id)
                
                # Add all requirements from then_add
                then_add = rule.get('then_add', [])
                confidence = rule.get('confidence', 0.8)
                
                for req_text in then_add:
                    generated.append({
                        "text": req_text,
                        "confidence": confidence,
                        "source_rule": rule_id,
                        "matched_keywords": matched_keywords,
                        "category": cls._infer_category(req_text)
                    })
        
        # Remove duplicates (by text)
        seen = set()
        unique_generated = []
        for req in generated:
            if req["text"] not in seen:
                seen.add(req["text"])
                unique_generated.append(req)
        
        return unique_generated
    
    @classmethod
    def _infer_category(cls, text: str) -> str:
        """Infer category from requirement text"""
        text_lower = text.lower()
        if "security" in text_lower or "encrypt" in text_lower or "pci" in text_lower:
            return "Security"
        if "gdpr" in text_lower or "privacy" in text_lower or "data" in text_lower:
            return "Compliance"
        if "tracking" in text_lower or "location" in text_lower or "gps" in text_lower:
            return "Location Services"
        if "notification" in text_lower or "push" in text_lower:
            return "Notifications"
        if "authentication" in text_lower or "login" in text_lower:
            return "Authentication"
        return "Infrastructure"
    
    @classmethod
    def expand_requirements(cls, existing_requirements: List[Dict], domain: str, rules: List[Dict]) -> List[Dict]:
        """
        Expand a list of existing requirements by applying rules to each
        Returns combined list of original + new requirements
        """
        all_texts = [req.get('text', '') for req in existing_requirements]
        combined_text = " ".join(all_texts)
        
        new_requirements = cls.apply_rules(combined_text, rules)
        
        # Also apply domain-specific mandatory requirements from knowledge base
        from backend.app.modules.module_4_knowledge_graph.knowledge_base_loader import KnowledgeBaseLoader
        loader = KnowledgeBaseLoader()
        domain_reqs = loader.get_domain_requirements(domain)
        
        for req in domain_reqs:
            # Check if requirement already exists (by keyword similarity)
            existing_texts_lower = [t.lower() for t in all_texts]
            req_text_lower = req.get('text', '').lower()
            if not any(req_text_lower in existing or existing in req_text_lower for existing in existing_texts_lower):
                new_requirements.append({
                    "text": req.get('text', ''),
                    "confidence": 0.95,
                    "source_rule": "domain_mandatory",
                    "matched_keywords": [],
                    "category": req.get('category', 'Core')
                })
        
        return new_requirements
