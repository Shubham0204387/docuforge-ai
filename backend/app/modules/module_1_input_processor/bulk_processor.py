"""Process multiple requirements from input"""
import re
from typing import List, Dict, Any

class BulkProcessor:
    """Extracts multiple requirements from text"""
    
    @staticmethod
    def extract_requirements(text: str) -> List[Dict[str, Any]]:
        """
        Extract individual requirements from text
        Returns list of {text: str, type: str, line_number: int}
        """
        requirements = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Skip if line is too short
            if len(line) < 5:
                continue
            
            # Detect requirement type based on formatting
            req_type = "unknown"
            
            # Bullet point
            if re.match(r'^[\s]*[-*•]', line):
                line = re.sub(r'^[\s]*[-*•]\s*', '', line)
                req_type = "bullet"
            # Numbered list
            elif re.match(r'^[\s]*\d+\.', line):
                line = re.sub(r'^[\s]*\d+\.\s*', '', line)
                req_type = "numbered"
            # Plain text with action verb
            elif any(verb in line.lower() for verb in ['shall', 'should', 'must', 'will', 'can', 'may']):
                req_type = "formal"
            else:
                req_type = "plain"
            
            requirements.append({
                "text": line,
                "type": req_type,
                "line_number": i + 1,
                "length": len(line)
            })
        
        return requirements
