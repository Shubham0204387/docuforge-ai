"""Generate resolution suggestions for detected conflicts"""
from typing import Dict, List

class ResolutionSuggester:
    """Provides actionable suggestions to resolve conflicts"""
    
    RESOLUTION_TEMPLATES = {
        "semantic_contradiction": [
            "Reconcile the conflicting terms by choosing one standard.",
            "Introduce a configuration option to support both behaviors.",
            "Clarify the context: under what conditions each applies."
        ],
        "numeric_contradiction": [
            "Negotiate a unified numeric threshold that satisfies both.",
            "Separate requirements into different operational modes (e.g., normal vs peak).",
            "Accept the stricter constraint if feasible."
        ],
        "technology_conflict": [
            "Evaluate which technology better meets overall project goals.",
            "Consider abstraction layer to support both (e.g., API gateway).",
            "Phase migration: use one now, plan to switch later."
        ],
        "resource_conflict": [
            "Adjust resource allocation to meet the higher requirement.",
            "Optimize application to reduce resource needs.",
            "Schedule resource-intensive tasks at different times."
        ],
        "priority_deadlock": [
            "Break the cycle by reordering dependencies.",
            "Merge the cyclically dependent requirements.",
            "Introduce a new intermediate requirement that satisfies both."
        ]
    }
    
    @classmethod
    def suggest(cls, conflict: Dict) -> List[str]:
        """Return resolution suggestions for a conflict"""
        conflict_type = conflict.get('type', 'semantic_contradiction')
        templates = cls.RESOLUTION_TEMPLATES.get(conflict_type, cls.RESOLUTION_TEMPLATES["semantic_contradiction"])
        
        # Add conflict-specific customizations
        suggestions = list(templates)
        if conflict_type == "semantic_contradiction":
            terms = conflict.get('details', {}).get('conflicting_terms', [])
            if terms:
                suggestions.insert(0, f"Replace '{terms[0]}' with a more precise term that doesn't conflict with '{terms[1]}'.")
        elif conflict_type == "technology_conflict":
            techs = conflict.get('details', {})
            if techs:
                suggestions.insert(0, f"Choose either {techs.get('tech1', 'unknown')} or {techs.get('tech2', 'unknown')} based on team expertise.")
        
        return suggestions[:3]  # Return top 3 suggestions
