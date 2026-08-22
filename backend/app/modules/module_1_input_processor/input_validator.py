"""Validate input for completeness and consistency"""
import re
from typing import Dict, Any, List

class InputValidator:
    """Validates user input quality"""
    
    MIN_LENGTH = 10
    MAX_LENGTH = 50000
    
    @staticmethod
    def validate(text: str) -> Dict[str, Any]:
        """
        Validate input text
        Returns: {is_valid: bool, issues: list, suggestions: list}
        """
        issues = []
        suggestions = []
        text = text.strip()
        
        # Check length
        if len(text) < InputValidator.MIN_LENGTH:
            issues.append(f"Input too short (minimum {InputValidator.MIN_LENGTH} characters)")
            suggestions.append("Add more details about your project requirements")
        
        if len(text) > InputValidator.MAX_LENGTH:
            issues.append(f"Input too long (maximum {InputValidator.MAX_LENGTH} characters)")
            suggestions.append("Summarize your requirements or upload as file")
        
        # Check for vague terms
        vague_terms = ['fast', 'slow', 'easy', 'hard', 'good', 'bad', 'secure', 'scalable']
        found_vague = [term for term in vague_terms if term in text.lower()]
        if found_vague:
            issues.append(f"Vague terms detected: {', '.join(found_vague)}")
            suggestions.append("Clarify vague terms (e.g., 'fast' → 'response time under 2 seconds')")
        
        # Check for missing actors
        actors = ['user', 'admin', 'customer', 'system', 'employee']
        found_actors = [actor for actor in actors if actor in text.lower()]
        if not found_actors:
            issues.append("No actors/users mentioned")
            suggestions.append("Specify who will use the system (users, admins, customers, etc.)")
        
        # Check for missing actions
        actions = ['create', 'read', 'update', 'delete', 'view', 'search', 'filter', 'process', 'generate']
        found_actions = [action for action in actions if action in text.lower()]
        if not found_actions:
            issues.append("No actions/functionality mentioned")
            suggestions.append("Describe what the system should DO (create, view, update, search, etc.)")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "stats": {
                "length": len(text),
                "word_count": len(text.split()),
                "vague_terms_count": len(found_vague)
            }
        }
