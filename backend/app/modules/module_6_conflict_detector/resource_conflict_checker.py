"""Detects conflicts in technology choices and resource allocations"""
import re
from typing import List, Dict, Any

class ResourceConflictChecker:
    """Identifies incompatible technology or resource requirements"""
    
    # Incompatible technology pairs
    TECH_CONFLICTS = [
        ("mysql", "postgresql"),
        ("mongodb", "sqlite"),
        ("react", "vue"),
        ("angular", "react"),
        ("aws", "azure"),
        ("docker", "virtualbox"),
        ("kubernetes", "docker swarm"),
        ("python", "java"),
        ("node.js", "php"),
        ("redis", "memcached"),
    ]
    
    # Resource constraint patterns - each is a tuple (pattern1, pattern2)
    RESOURCE_CONFLICTS = [
        (r'(\d+)\s*GB\s*RAM', r'(\d+)\s*GB\s*RAM'),  # Different RAM requirements
        (r'(\d+)\s*cores?', r'(\d+)\s*cores?'),       # Different CPU core counts
        (r'(\d+)\s*GB\s*storage', r'(\d+)\s*GB\s*storage'),  # Storage
    ]
    
    @classmethod
    def detect_conflicts(cls, requirements: List[Dict]) -> List[Dict]:
        """
        Detect resource and technology conflicts
        Returns list of conflict objects
        """
        conflicts = []
        texts = [req.get('text', '').lower() for req in requirements]
        req_ids = [req.get('requirement_id', f"REQ_{i}") for i, req in enumerate(requirements)]
        
        # Check technology conflicts
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                for (tech1, tech2) in cls.TECH_CONFLICTS:
                    if tech1 in texts[i] and tech2 in texts[j]:
                        conflicts.append({
                            "type": "technology_conflict",
                            "requirement_1": req_ids[i],
                            "requirement_2": req_ids[j],
                            "description": f"Technology '{tech1}' is incompatible with '{tech2}'",
                            "severity": "HIGH",
                            "details": {"tech1": tech1, "tech2": tech2}
                        })
                    if tech2 in texts[i] and tech1 in texts[j]:
                        conflicts.append({
                            "type": "technology_conflict",
                            "requirement_1": req_ids[i],
                            "requirement_2": req_ids[j],
                            "description": f"Technology '{tech2}' is incompatible with '{tech1}'",
                            "severity": "HIGH",
                            "details": {"tech1": tech2, "tech2": tech1}
                        })
        
        # Check resource numeric conflicts - fix: pattern is a tuple of two patterns
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                for (pattern1, pattern2) in cls.RESOURCE_CONFLICTS:
                    match1 = re.search(pattern1, texts[i])
                    match2 = re.search(pattern2, texts[j])
                    if match1 and match2:
                        val1 = int(match1.group(1))
                        val2 = int(match2.group(1))
                        if abs(val1 - val2) > val1 * 0.5:  # More than 50% difference
                            conflicts.append({
                                "type": "resource_conflict",
                                "requirement_1": req_ids[i],
                                "requirement_2": req_ids[j],
                                "description": f"Inconsistent resource requirements: {val1} vs {val2}",
                                "severity": "MEDIUM",
                                "details": {"value1": val1, "value2": val2}
                            })
        
        return conflicts
