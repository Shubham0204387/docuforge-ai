"""Extract entities (actors, systems, data objects) from requirement text"""
import re
import spacy
from typing import List, Dict, Any, Set

# Load spaCy model (small model for M5 performance)
nlp = spacy.load("en_core_web_sm")

class EntityRecognizer:
    """Identifies actors, actions, objects, and conditions in text"""
    
    # Predefined actor keywords
    ACTOR_KEYWORDS = {
        "user", "admin", "customer", "employee", "manager", "guest", "visitor",
        "system", "server", "client", "device", "mobile", "web", "api", "service",
        "driver", "restaurant", "vendor", "partner", "supplier"
    }
    
    # Action verbs (common requirement actions)
    ACTION_VERBS = {
        "create", "read", "update", "delete", "view", "search", "filter", "sort",
        "upload", "download", "generate", "process", "calculate", "compute",
        "send", "receive", "notify", "alert", "log", "track", "monitor", "report",
        "authenticate", "authorize", "validate", "verify", "encrypt", "decrypt",
        "export", "import", "sync", "backup", "restore", "schedule", "cancel"
    }
    
    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        """
        Extract entities from requirement text
        Returns: {
            "actors": list,
            "actions": list,
            "objects": list,
            "conditions": list,
            "spacy_entities": list (PERSON, ORG, etc.)
        }
        """
        doc = nlp(text)
        text_lower = text.lower()
        
        # Extract using spaCy NER
        spacy_entities = []
        for ent in doc.ents:
            spacy_entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        # Extract actors (noun chunks that match actor keywords or are persons)
        actors = set()
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            # Check against actor keywords
            for keyword in cls.ACTOR_KEYWORDS:
                if keyword in chunk_text:
                    actors.add(chunk.text)
                    break
            # Also add PERSON entities from spaCy
            for ent in doc.ents:
                if ent.label_ == "PERSON" and ent.text.lower() in chunk_text:
                    actors.add(ent.text)
        
        # Extract actions (verbs that match action keywords or are root verbs)
        actions = set()
        for token in doc:
            if token.pos_ == "VERB" or (token.pos_ == "AUX" and token.dep_ == "ROOT"):
                action = token.lemma_.lower()
                if action in cls.ACTION_VERBS or len(action) > 3:
                    actions.add(action)
        
        # Extract objects (nouns that are direct objects or follow prepositions)
        objects = set()
        for token in doc:
            if token.dep_ in ("dobj", "pobj", "attr"):
                objects.add(token.text)
            # Also add noun chunks that are not actors
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text
                if chunk_text not in actors and len(chunk_text) > 2:
                    objects.add(chunk_text)
        
        # Extract conditions (clauses starting with if, when, while, where)
        conditions = []
        condition_patterns = [
            r'\bif\s+([^.]+?)(?:,|\.|;|$)',
            r'\bwhen\s+([^.]+?)(?:,|\.|;|$)',
            r'\bwhere\s+([^.]+?)(?:,|\.|;|$)',
            r'\bprovided that\s+([^.]+?)(?:,|\.|;|$)'
        ]
        for pattern in condition_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            conditions.extend([m.strip() for m in matches])
        
        return {
            "actors": list(actors),
            "actions": list(actions),
            "objects": list(objects),
            "conditions": conditions,
            "spacy_entities": spacy_entities
        }
    
    @classmethod
    def enrich_requirement(cls, requirement_text: str, existing_entities: Dict = None) -> Dict:
        """Enrich a requirement with extracted entities and suggestions"""
        entities = cls.extract_entities(requirement_text)
        
        # Generate suggestions for missing elements
        suggestions = []
        if not entities["actors"]:
            suggestions.append("Specify who performs this action (user, system, admin, etc.)")
        if not entities["actions"]:
            suggestions.append("Specify what action should be performed (create, view, update, delete, etc.)")
        if not entities["objects"]:
            suggestions.append("Specify what data or item this requirement acts upon")
        
        return {
            "original_text": requirement_text,
            "entities": entities,
            "suggestions": suggestions,
            "has_complete_elements": len(entities["actors"]) > 0 and len(entities["actions"]) > 0
        }
