"""Apply rules and manage confidence scoring"""
from typing import List, Dict, Any
from backend.app.modules.module_4_knowledge_graph.inference_engine import InferenceEngine

class RuleApplicator:
    """Orchestrates rule application and result merging"""
    
    @classmethod
    def apply_all(cls, requirements: List[Dict], domain: str, rules: List[Dict]) -> Dict[str, Any]:
        """
        Apply all inference and pattern matching
        Returns: {
            "expanded_requirements": list,
            "applied_rules": list,
            "statistics": dict
        }
        """
        # Expand using inference engine
        new_reqs = InferenceEngine.expand_requirements(requirements, domain, rules)
        
        # Apply pattern matching for additional suggestions (optional)
        from backend.app.modules.module_4_knowledge_graph.pattern_matcher import PatternMatcher
        from backend.app.modules.module_4_knowledge_graph.knowledge_base_loader import KnowledgeBaseLoader
        
        loader = KnowledgeBaseLoader()
        patterns = loader.get_domain_patterns(domain)
        
        pattern_suggestions = []
        for req in requirements:
            text = req.get('text', '')
            matches = PatternMatcher.match(text, patterns)
            for match in matches:
                if match['matched']:
                    for sugg in match.get('requirements', []):
                        pattern_suggestions.append({
                            "text": sugg,
                            "confidence": match['similarity'] * 0.9,
                            "source_pattern": match['pattern'],
                            "category": "Pattern Suggestion"
                        })
        
        # Merge and deduplicate new_reqs and pattern_suggestions
        all_new = new_reqs.copy()
        seen_texts = {r['text'] for r in all_new}
        for sugg in pattern_suggestions:
            if sugg['text'] not in seen_texts:
                all_new.append(sugg)
                seen_texts.add(sugg['text'])
        
        # Sort by confidence descending
        all_new.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Collect applied rules for audit
        applied_rules = list(set([r.get('source_rule', 'unknown') for r in all_new if r.get('source_rule')]))
        
        return {
            "expanded_requirements": all_new,
            "applied_rules": applied_rules,
            "statistics": {
                "original_count": len(requirements),
                "expanded_count": len(all_new),
                "total_count": len(requirements) + len(all_new)
            }
        }
