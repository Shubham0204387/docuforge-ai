"""Convert natural language requirements to IEEE 830 formal style"""
import re
from typing import Dict, Any, List
from backend.app.modules.module_5_requirement_generator.template_selector import TemplateSelector

class FormalConverter:
    """Transforms informal requirement text into formal IEEE 830 language"""
    
    # Common informal patterns and their formal replacements
    INFORMAL_TO_FORMAL = {
        r'\bcan\b': 'shall be able to',
        r'\bmay\b': 'shall',
        r'\bshould\b': 'shall',
        r'\bmight\b': 'shall',
        r'\bneed to\b': 'shall',
        r'\bmust\b': 'shall',
        r'\bwant to\b': 'shall be able to',
        r'\bwill\b': 'shall',
        r'\ballow\s+(\w+)\s+to\b': r'allow \1 to',
    }
    
    @classmethod
    def convert(cls, text: str, req_type: str = "functional", subtype: str = None) -> str:
        """
        Convert informal text to formal IEEE 830 requirement
        Returns formalized string
        """
        original = text.strip()
        
        # Ensure first letter capital and end with period
        if original and original[0].islower():
            original = original[0].upper() + original[1:]
        if not original.endswith('.'):
            original += '.'
        
        # Apply informal to formal replacements
        formal = original
        for pattern, replacement in cls.INFORMAL_TO_FORMAL.items():
            formal = re.sub(pattern, replacement, formal, flags=re.IGNORECASE)
        
        # If text doesn't start with "The system", add appropriate prefix
        if not re.match(r'^(The system|System|It)', formal, re.IGNORECASE):
            # Extract action and object if possible
            words = formal.split()
            if len(words) > 0:
                # Try to find a verb
                for i, word in enumerate(words):
                    if word.endswith('e') or word in ['allow', 'provide', 'support', 'enable']:
                        action_phrase = ' '.join(words[i:])
                        formal = f"The system shall {action_phrase}"
                        break
                else:
                    formal = f"The system shall {formal}"
        
        # Remove redundant "shall shall"
        formal = re.sub(r'\bshall\s+shall\b', 'shall', formal, flags=re.IGNORECASE)
        
        # Ensure proper IEEE 830 format: "The system shall ..."
        if not formal.startswith('The system'):
            formal = 'The system ' + formal[0].lower() + formal[1:] if formal else formal
        
        # Capitalize first letter of sentence
        formal = formal[0].upper() + formal[1:]
        
        return formal
    
    @classmethod
    def batch_convert(cls, requirements: List[Dict]) -> List[Dict]:
        """Convert multiple requirements at once"""
        results = []
        for req in requirements:
            text = req.get('text', '')
            req_type = req.get('type', 'functional')
            subtype = req.get('subtype')
            formal_text = cls.convert(text, req_type, subtype)
            results.append({
                "original": text,
                "formal": formal_text,
                "requirement_id": req.get('requirement_id')
            })
        return results
