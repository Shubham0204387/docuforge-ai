"""Evaluate requirements against SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)"""
import re
from typing import Dict, Any

class SMARTCriteriaChecker:
    @classmethod
    def check(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        results = {}
        
        # Specific: has actors or concrete nouns
        specific_score = 50
        if re.search(r'\b(user|admin|customer|system|employee|manager|device|api|database|server)\b', text_lower):
            specific_score += 30
        if len(text.split()) > 8:
            specific_score += 10
        if any(word in text_lower for word in ['the system', 'shall', 'must', 'should']):
            specific_score += 10
        results['specific'] = min(100, specific_score)
        
        # Measurable: contains numbers, metrics, time, percentages
        measurable_score = 0
        patterns = [r'\d+', r'\d+\s*%', r'\d+\s*(seconds?|ms|milliseconds?|minutes?|hours?|days?)',
                    r'\d+\s*(MB|GB|TB|KB)', r'\d+\s*users?', r'(under|less than|more than|over|within|at least|at most)\s*\d+']
        for p in patterns:
            if re.search(p, text_lower):
                measurable_score += 20
        results['measurable'] = min(100, measurable_score)
        
        # Achievable: check for unrealistic terms
        achievable_score = 80
        unrealistic = ['perfect', 'impossible', 'never', 'always', 'all', 'every single', 'flawless', 'bug-free',
                       'millions of concurrent', 'infinite', 'unlimited', 'zero latency']
        for term in unrealistic:
            if term in text_lower:
                achievable_score -= 30
        results['achievable'] = max(0, achievable_score)
        
        # Relevant: default high (can be enhanced later)
        results['relevant'] = 85
        
        # Time-bound: contains deadline or schedule
        time_bound_score = 0
        time_patterns = [r'by\s+\w+\s+\d{1,2},?\s+\d{4}', r'within\s+\d+\s+(days?|weeks?|months?)',
                         r'before\s+\w+\s+\d{4}', r'Q[1-4]\s+\d{4}', r'phase\s+\d+', r'release\s+[\d.]+']
        for p in time_patterns:
            if re.search(p, text_lower, re.IGNORECASE):
                time_bound_score = 100
                break
        results['time_bound'] = time_bound_score
        
        overall = sum(results.values()) / len(results)
        results['overall'] = round(overall, 1)
        grade = 'A' if overall >= 80 else 'B' if overall >= 65 else 'C' if overall >= 50 else 'D'
        results['grade'] = grade
        results['summary'] = f"SMART Score: {overall:.1f} ({grade})"
        return results
