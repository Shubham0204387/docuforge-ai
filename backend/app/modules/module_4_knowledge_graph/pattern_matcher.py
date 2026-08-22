"""Match user requirements to known patterns"""
import re
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

class PatternMatcher:
    """Matches requirement text against stored patterns"""
    
    @classmethod
    def match(cls, text: str, patterns: List[Dict]) -> List[Dict]:
        """
        Match text against list of patterns
        Returns list of matches with similarity scores
        """
        text_lower = text.lower()
        matches = []
        
        for pattern_obj in patterns:
            pattern = pattern_obj.get('pattern', '')
            pattern_lower = pattern.lower()
            
            # Exact match
            if pattern_lower in text_lower:
                matches.append({
                    "pattern": pattern,
                    "similarity": 1.0,
                    "matched": True,
                    "requirements": pattern_obj.get('requirements', [])
                })
            # Fuzzy match
            else:
                similarity = cls._fuzzy_match(text_lower, pattern_lower)
                if similarity > 0.6:
                    matches.append({
                        "pattern": pattern,
                        "similarity": similarity,
                        "matched": similarity > 0.8,
                        "requirements": pattern_obj.get('requirements', [])
                    })
        
        # Sort by similarity descending
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches
    
    @classmethod
    def _fuzzy_match(cls, text: str, pattern: str) -> float:
        """Calculate fuzzy similarity between text and pattern"""
        # Check for word overlap
        text_words = set(text.split())
        pattern_words = set(pattern.split())
        if not pattern_words:
            return 0.0
        
        overlap = len(text_words.intersection(pattern_words))
        union = len(text_words.union(pattern_words))
        word_overlap = overlap / union if union > 0 else 0.0
        
        # Use SequenceMatcher for string similarity
        string_sim = SequenceMatcher(None, text, pattern).ratio()
        
        # Combine scores
        return (word_overlap * 0.6) + (string_sim * 0.4)
    
    @classmethod
    def match_keywords(cls, text: str, keywords: List[str]) -> List[str]:
        """Check which keywords are present in text"""
        text_lower = text.lower()
        return [kw for kw in keywords if kw in text_lower]
