"""Select appropriate IEEE 830 template based on requirement type"""
from typing import Dict, Any

class TemplateSelector:
    """Selects the correct template for formalizing a requirement"""
    
    # IEEE 830 templates for different requirement types
    FUNCTIONAL_TEMPLATES = [
        "The system shall {action} {object}",
        "The system shall allow {actor} to {action} {object}",
        "The system shall provide {actor} with the ability to {action} {object}",
        "The system shall support {action} of {object} by {actor}"
    ]
    
    NONFUNCTIONAL_TEMPLATES = {
        "performance": "The system shall {action} within {metric}",
        "security": "The system shall ensure {security_property} for {object}",
        "usability": "The system shall be {usability_criteria} for {actor}",
        "reliability": "The system shall maintain {reliability_metric} uptime",
        "scalability": "The system shall support {scale_metric} concurrent {actor}s",
        "maintainability": "The system shall be {maintainability_metric}"
    }
    
    CONSTRAINT_TEMPLATES = [
        "The system must comply with {constraint}",
        "The system shall be implemented using {technology}",
        "The system shall adhere to {standard}",
        "The system is constrained by {limitation}"
    ]
    
    @classmethod
    def select_template(cls, requirement_type: str, subtype: str = None) -> str:
        """Select appropriate template based on requirement type"""
        if requirement_type == "functional":
            return cls.FUNCTIONAL_TEMPLATES[0]  # Default functional template
        elif requirement_type == "non_functional":
            if subtype and subtype in cls.NONFUNCTIONAL_TEMPLATES:
                return cls.NONFUNCTIONAL_TEMPLATES[subtype]
            return cls.NONFUNCTIONAL_TEMPLATES["performance"]  # Default NFR
        elif requirement_type == "constraint":
            return cls.CONSTRAINT_TEMPLATES[0]
        else:
            return cls.FUNCTIONAL_TEMPLATES[0]
    
    @classmethod
    def get_all_templates(cls) -> Dict[str, Any]:
        """Return all available templates for reference"""
        return {
            "functional": cls.FUNCTIONAL_TEMPLATES,
            "non_functional": cls.NONFUNCTIONAL_TEMPLATES,
            "constraint": cls.CONSTRAINT_TEMPLATES
        }
