"""Detect vague terms, weasel words, and passive voice"""
import re
from typing import Dict, Any

class AmbiguityDetector:
    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        vague_terms = {
            "performance": ["fast", "quick", "slow", "efficient", "high-performance", "responsive"],
            "quantity": ["many", "few", "several", "numerous", "countless", "lot of", "plenty"],
            "quality": ["good", "bad", "excellent", "poor", "user-friendly", "intuitive", "robust"],
            "time": ["real-time", "immediate", "soon", "asap", "quickly", "eventually"],
            "uncertainty": ["approximately", "around", "roughly", "about", "maybe", "perhaps", "possibly"],
            "weasel": ["it is believed", "it is thought", "some say", "many experts", "commonly known"]
        }
        ambiguous_found = []
        categories_found = {}
        for cat, terms in vague_terms.items():
            for term in terms:
                if term in text_lower:
                    ambiguous_found.append(term)
                    categories_found.setdefault(cat, []).append(term)
        
        # Passive voice detection
        passive_count = len(re.findall(r'\b(be|is|are|was|were|been|being)\s+(\w+ed|\w+en|\w+t)\b', text_lower))
        
        penalty = len(ambiguous_found) * 8 + passive_count * 5
        clarity_score = max(0, 100 - penalty)
        return {
            "has_ambiguity": len(ambiguous_found) > 0,
            "ambiguous_terms": list(set(ambiguous_found)),
            "categories": categories_found,
            "passive_voice_count": passive_count,
            "clarity_score": clarity_score,
            "summary": f"Clarity: {clarity_score}/100, Ambiguous terms: {len(set(ambiguous_found))}, Passive voice: {passive_count}"
        }
