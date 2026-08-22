"""NLP service integrating all Module 3 components"""
from backend.app.modules.module_3_nlp import (
    EntityRecognizer, SemanticAnalyzer, IntentClassifier, ContextAnalyzer
)
from typing import Dict, Any, List

class NLPService:
    """Service that applies all NLP analyses to a requirement"""
    
    @classmethod
    def analyze_requirement(cls, text: str, domain: str = "general", previous_texts: List[str] = None) -> Dict[str, Any]:
        """Run complete NLP analysis on a single requirement"""
        
        # 1. Context analysis (domain term resolution, pronoun resolution)
        context = ContextAnalyzer.analyze_context(text, domain, previous_texts)
        
        # Use resolved text for further analysis
        analysis_text = context["resolved_text"]
        
        # 2. Entity recognition
        entities = EntityRecognizer.extract_entities(analysis_text)
        
        # 3. Semantic analysis
        semantics = SemanticAnalyzer.analyze(analysis_text)
        
        # 4. Intent classification
        intent = IntentClassifier.classify(analysis_text)
        
        # 5. Enrich requirement with suggestions
        enriched = EntityRecognizer.enrich_requirement(analysis_text, entities)
        
        return {
            "original_text": text,
            "analyzed_text": analysis_text,
            "entities": entities,
            "semantics": semantics,
            "intent": intent,
            "implicit_requirements": context["implicit_requirements"],
            "completeness_suggestions": enriched["suggestions"],
            "has_complete_structure": semantics["has_complete_structure"] and enriched["has_complete_elements"]
        }
    
    @classmethod
    def batch_analyze(cls, requirements: List[Dict], domain: str) -> List[Dict]:
        """Analyze multiple requirements, maintaining context across them"""
        results = []
        previous_texts = []
        
        for req in requirements:
            text = req.get("text", "")
            analysis = cls.analyze_requirement(text, domain, previous_texts)
            previous_texts.append(text)
            results.append({
                "requirement_id": req.get("id", req.get("requirement_id")),
                "analysis": analysis
            })
        
        return results
