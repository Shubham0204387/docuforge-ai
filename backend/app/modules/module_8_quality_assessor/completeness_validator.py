"""Check if requirement has actor, action, condition, success criteria"""
import re
from typing import Dict, Any

class CompletenessValidator:
    @classmethod
    def validate(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        missing = []
        has_actor = any(actor in text_lower for actor in ['user', 'admin', 'customer', 'system', 'employee', 'manager'])
        if not has_actor:
            missing.append("actor")
        has_action = any(action in text_lower for action in ['shall', 'must', 'should', 'will', 'can', 'may', 'allow', 'enable'])
        if not has_action:
            missing.append("action verb")
        has_condition = any(cond in text_lower for cond in ['if', 'when', 'while', 'where', 'provided that'])
        has_success = any(crit in text_lower for crit in ['verify', 'validate', 'check', 'ensure', 'confirm', 'test', 'measure'])
        if not has_success:
            missing.append("success criteria")
        completeness_score = 100
        if not has_actor:
            completeness_score -= 25
        if not has_action:
            completeness_score -= 30
        if not has_success:
            completeness_score -= 25
        completeness_score = max(0, completeness_score)
        return {
            "has_actor": has_actor,
            "has_action": has_action,
            "has_condition": has_condition,
            "has_success_criteria": has_success,
            "missing_elements": missing,
            "completeness_score": completeness_score,
            "summary": f"Completeness: {completeness_score}/100, Missing: {', '.join(missing) if missing else 'None'}"
        }
