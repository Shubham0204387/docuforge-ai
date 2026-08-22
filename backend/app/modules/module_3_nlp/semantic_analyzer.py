"""Semantic role labeling to understand relationships in requirements"""
import re
import spacy
from typing import Dict, Any, List, Optional

nlp = spacy.load("en_core_web_sm")

class SemanticAnalyzer:
    """Identifies subject-verb-object relationships and semantic roles"""
    
    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        """
        Perform semantic analysis on requirement text
        Returns: {
            "subject": str,
            "verb": str,
            "object": str,
            "modifiers": list,
            "negation": bool,
            "passive": bool,
            "dependency_tree": dict
        }
        """
        doc = nlp(text)
        
        # Find the main subject, verb, and object
        subject = None
        verb = None
        obj = None
        modifiers = []
        negation = False
        passive = False
        
        for token in doc:
            # Check for negation
            if token.dep_ == "neg":
                negation = True
            
            # Find root verb
            if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
                verb = token.lemma_
                # Check if passive
                for child in token.children:
                    if child.dep_ == "auxpass":
                        passive = True
            
            # Find subject (nsubj or nsubjpass)
            if token.dep_ in ("nsubj", "nsubjpass"):
                # Get the full noun phrase
                subject = token.text
                # Expand to full span if part of a noun chunk
                for chunk in doc.noun_chunks:
                    if token in chunk:
                        subject = chunk.text
                        break
            
            # Find object (dobj or pobj)
            if token.dep_ in ("dobj", "pobj", "attr"):
                obj = token.text
                for chunk in doc.noun_chunks:
                    if token in chunk:
                        obj = chunk.text
                        break
            
            # Collect adjectival and adverbial modifiers
            if token.dep_ in ("amod", "advmod", "prep"):
                modifiers.append(token.text)
        
        # Build dependency tree summary
        dep_tree = {}
        for token in doc:
            dep_tree[token.text] = {
                "pos": token.pos_,
                "dep": token.dep_,
                "head": token.head.text
            }
        
        return {
            "subject": subject,
            "verb": verb,
            "object": obj,
            "modifiers": list(set(modifiers)),
            "negation": negation,
            "passive": passive,
            "dependency_tree": dep_tree,
            "has_complete_structure": subject is not None and verb is not None
        }
    
    @classmethod
    def extract_relationships(cls, text: str) -> List[Dict]:
        """Extract all subject-verb-object triples from text"""
        doc = nlp(text)
        relationships = []
        
        for sent in doc.sents:
            sent_text = sent.text
            # Find all verbs in sentence
            verbs = [token for token in sent if token.pos_ == "VERB"]
            for verb_token in verbs:
                # Find subject for this verb
                subject = None
                for child in verb_token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = child.text
                        # Get full noun phrase
                        for chunk in sent.noun_chunks:
                            if child in chunk:
                                subject = chunk.text
                                break
                
                # Find object for this verb
                obj = None
                for child in verb_token.children:
                    if child.dep_ in ("dobj", "pobj", "attr"):
                        obj = child.text
                        for chunk in sent.noun_chunks:
                            if child in chunk:
                                obj = chunk.text
                                break
                
                if subject and verb_token.lemma_:
                    relationships.append({
                        "subject": subject,
                        "verb": verb_token.lemma_,
                        "object": obj,
                        "sentence": sent_text[:100]
                    })
        
        return relationships
