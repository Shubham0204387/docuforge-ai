"""Detects logical contradictions between requirements"""
import re
from typing import List, Dict, Any, Tuple

class SemanticConflictAnalyzer:
    """Identifies contradictory statements in requirements"""
    
    # Pairs of opposite actions/conditions – now more robust with normalization
    OPPOSITE_PAIRS = [
        ("auto", "manual"),
        ("automatic", "manual"),
        ("auto-save", "confirm before save"),
        ("auto-save", "require confirmation"),
        ("auto-save", "require user confirmation"),
        ("save automatically", "require confirmation"),
        ("save automatically", "require user confirmation"),
        ("real-time", "batch"),
        ("synchronous", "asynchronous"),
        ("encrypt", "plain text"),
        ("encrypted", "unencrypted"),
        ("authenticated", "public"),
        ("private", "public"),
        ("delete", "archive"),
        ("permanent", "temporary"),
        ("allow", "block"),
        ("enable", "disable"),
        ("fast", "slow"),
        ("high performance", "low resource"),
    ]
    
    SEVERITY_MAP = {
        "direct_contradiction": "HIGH",
        "partial_overlap": "MEDIUM",
        "potential_issue": "LOW"
    }
    
    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Remove common stop words and normalize for better matching"""
        # Remove common stop words like "user", "the", "a", "an"
        stop_words = ['user', 'the', 'a', 'an', 'any', 'all', 'each', 'every']
        words = text.lower().split()
        filtered = [w for w in words if w not in stop_words]
        return ' '.join(filtered)
    
    @classmethod
    def detect_conflicts(cls, requirements: List[Dict]) -> List[Dict]:
        """Detect semantic conflicts between requirements"""
        conflicts = []
        texts = [req.get('text', '').lower() for req in requirements]
        req_ids = [req.get('requirement_id', f"REQ_{i}") for i, req in enumerate(requirements)]
        
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                normalized_i = cls.normalize_text(texts[i])
                normalized_j = cls.normalize_text(texts[j])
                conflict = cls._check_pair(normalized_i, normalized_j, req_ids[i], req_ids[j])
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    @classmethod
    def _check_pair(cls, text1: str, text2: str, id1: str, id2: str) -> Dict:
        """Check a pair of requirements for contradiction"""
        for (word_a, word_b) in cls.OPPOSITE_PAIRS:
            # Check both orders
            if word_a in text1 and word_b in text2:
                return {
                    "type": "semantic_contradiction",
                    "requirement_1": id1,
                    "requirement_2": id2,
                    "description": f"'{word_a}' conflicts with '{word_b}'",
                    "severity": cls.SEVERITY_MAP["direct_contradiction"],
                    "details": {
                        "text_1": text1,
                        "text_2": text2,
                        "conflicting_terms": [word_a, word_b]
                    }
                }
            if word_b in text1 and word_a in text2:
                return {
                    "type": "semantic_contradiction",
                    "requirement_1": id1,
                    "requirement_2": id2,
                    "description": f"'{word_b}' conflicts with '{word_a}'",
                    "severity": cls.SEVERITY_MAP["direct_contradiction"],
                    "details": {
                        "text_1": text1,
                        "text_2": text2,
                        "conflicting_terms": [word_b, word_a]
                    }
                }
        
        # Numeric contradiction check (unchanged)
        numeric_conflict = cls._check_numeric_conflict(text1, text2)
        if numeric_conflict:
            return {
                "type": "numeric_contradiction",
                "requirement_1": id1,
                "requirement_2": id2,
                "description": numeric_conflict["description"],
                "severity": cls.SEVERITY_MAP["direct_contradiction"],
                "details": numeric_conflict
            }
        
        return None
    
    @classmethod
    def _check_numeric_conflict(cls, text1: str, text2: str) -> Dict:
        """Check for conflicting numeric constraints (e.g., response time ranges)"""
        patterns = [
            (r'under\s+(\d+)\s*(seconds?|ms|minutes?)', 'less_than'),
            (r'less than\s+(\d+)\s*(seconds?|ms|minutes?)', 'less_than'),
            (r'within\s+(\d+)\s*(seconds?|ms|minutes?)', 'less_than'),
            (r'over\s+(\d+)\s*(seconds?|ms|minutes?)', 'greater_than'),
            (r'more than\s+(\d+)\s*(seconds?|ms|minutes?)', 'greater_than'),
            (r'at least\s+(\d+)\s*(seconds?|ms|minutes?)', 'greater_equal'),
            (r'at most\s+(\d+)\s*(seconds?|ms|minutes?)', 'less_equal'),
        ]
        
        def extract(text):
            for pattern, op in patterns:
                match = re.search(pattern, text)
                if match:
                    return {"value": int(match.group(1)), "unit": match.group(2), "op": op}
            return None
        
        constraint1 = extract(text1)
        constraint2 = extract(text2)
        
        if constraint1 and constraint2 and constraint1["unit"] == constraint2["unit"]:
            if constraint1["op"] in ("less_than", "less_equal") and constraint2["op"] in ("greater_than", "greater_equal"):
                if constraint1["value"] <= constraint2["value"]:
                    return {
                        "description": f"Requirement says '{constraint1['value']} {constraint1['unit']}' but also requires more than {constraint2['value']} {constraint2['unit']}",
                        "value1": constraint1["value"],
                        "value2": constraint2["value"],
                        "unit": constraint1["unit"]
                    }
        return None
