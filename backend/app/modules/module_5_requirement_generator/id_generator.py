"""Generate unique requirement IDs following IEEE 830 pattern"""
import re
from typing import Dict, List, Set

class IDGenerator:
    """Generates sequential requirement IDs (FR-001, NFR-001, CON-001)"""
    
    # Prefixes for different requirement types
    PREFIX_MAP = {
        "functional": "FR",
        "non_functional": "NFR",
        "constraint": "CON",
        "inferred": "INF",
        "user_input": "UR"
    }
    
    def __init__(self):
        self.counters = {prefix: 0 for prefix in self.PREFIX_MAP.values()}
        self.used_ids = set()
    
    def reset(self):
        """Reset counters (useful for new projects)"""
        self.counters = {prefix: 0 for prefix in self.PREFIX_MAP.values()}
        self.used_ids = set()
    
    def generate_id(self, req_type: str, existing_ids: List[str] = None) -> str:
        """
        Generate a unique requirement ID
        Returns: FR-001, NFR-010, etc.
        """
        prefix = self.PREFIX_MAP.get(req_type, "FR")
        
        # Update counter based on existing IDs if provided
        if existing_ids:
            self._sync_counters(existing_ids)
        
        # Increment counter
        self.counters[prefix] += 1
        
        # Generate ID
        new_id = f"{prefix}-{self.counters[prefix]:03d}"
        
        # Ensure uniqueness (rare collision)
        while new_id in self.used_ids:
            self.counters[prefix] += 1
            new_id = f"{prefix}-{self.counters[prefix]:03d}"
        
        self.used_ids.add(new_id)
        return new_id
    
    def _sync_counters(self, existing_ids: List[str]):
        """Synchronize counters with existing IDs"""
        for req_id in existing_ids:
            match = re.match(r'([A-Z]+)-(\d+)', req_id)
            if match:
                prefix = match.group(1)
                num = int(match.group(2))
                if prefix in self.counters:
                    self.counters[prefix] = max(self.counters[prefix], num)
                self.used_ids.add(req_id)
    
    def generate_for_requirements(self, requirements: List[Dict], existing_ids: List[str] = None) -> List[Dict]:
        """Generate IDs for a list of requirements"""
        if existing_ids:
            self._sync_counters(existing_ids)
        
        results = []
        for req in requirements:
            req_type = req.get('type', 'functional')
            req_id = self.generate_id(req_type, existing_ids)
            results.append({
                "requirement_id": req_id,
                "original_text": req.get('text', ''),
                "type": req_type
            })
        return results
    
    @classmethod
    def extract_number(cls, req_id: str) -> int:
        """Extract numeric part from requirement ID"""
        match = re.search(r'\d+', req_id)
        return int(match.group()) if match else 0
