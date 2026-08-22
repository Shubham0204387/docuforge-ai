"""Detect input format (text, JSON, CSV, DOCX)"""
import json
import re
from typing import Dict, Any

class FormatDetector:
    """Detects the format of user input"""
    
    @staticmethod
    def detect(text: str) -> Dict[str, Any]:
        """
        Detect format of input text
        Returns: {format: str, confidence: float, details: dict}
        """
        text = text.strip()
        
        # Check for JSON
        if text.startswith('{') and text.endswith('}'):
            try:
                json.loads(text)
                return {"format": "json", "confidence": 0.95, "details": {"is_json": True}}
            except:
                pass
        
        # Check for CSV (has commas and line breaks)
        if ',' in text and '\n' in text:
            lines = text.split('\n')
            if len(lines) > 1 and lines[0].count(',') > 0:
                return {"format": "csv", "confidence": 0.85, "details": {"rows": len(lines)}}
        
        # Check for bullet points or numbered list
        if re.search(r'^[\s]*[-*•]', text, re.MULTILINE) or re.search(r'^[\s]*\d+\.', text, re.MULTILINE):
            return {"format": "bulleted_list", "confidence": 0.9, "details": {"has_bullets": True}}
        
        # Default to plain text
        return {"format": "text", "confidence": 0.95, "details": {"length": len(text)}}
