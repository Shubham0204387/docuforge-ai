"""Build and analyze dependency graphs between requirements"""
from typing import List, Dict, Set, Tuple

class DependencyMapper:
    """Constructs requirement dependencies and critical path"""
    
    # Heuristic keywords to infer dependencies
    DEPENDENCY_PATTERNS = [
        (r'after (.+?)(?:,|\.|$)', 'after'),
        (r'once (.+?) (?:is|has|has been)', 'after'),
        (r'requires (.+?)(?:,|\.|$)', 'requires'),
        (r'depends on (.+?)(?:,|\.|$)', 'depends'),
        (r'before (.+?)(?:,|\.|$)', 'before'),
    ]
    
    @classmethod
    def build_dependency_graph(cls, requirements: List[Dict]) -> Dict:
        """
        Build directed graph of requirements
        Returns: {
            "graph": {req_id: [dependent_ids]},
            "critical_path": [req_id_chain],
            "parallel_groups": [[req_ids]]
        }
        """
        # Create mapping from requirement_id to index and text
        id_to_text = {r['requirement_id']: r['text'] for r in requirements}
        req_ids = [r['requirement_id'] for r in requirements]
        
        graph = {rid: set() for rid in req_ids}
        
        # Use simple keyword matching: if ID mentioned in text -> add edge
        for rid, text in id_to_text.items():
            text_lower = text.lower()
            for other_rid in req_ids:
                if other_rid != rid and other_rid.lower() in text_lower:
                    graph[rid].add(other_rid)
        
        # Also check explicit patterns
        for rid, text in id_to_text.items():
            for pattern, _ in cls.DEPENDENCY_PATTERNS:
                import re
                matches = re.findall(pattern, text.lower())
                for match in matches:
                    for other_rid in req_ids:
                        if match in other_rid.lower() or match in id_to_text.get(other_rid, '').lower():
                            graph[rid].add(other_rid)
        
        # Find longest path (critical path) using DFS
        def longest_path(node, visited, memo):
            if node in memo:
                return memo[node]
            visited.add(node)
            max_len = 0
            max_path = [node]
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    sub_len, sub_path = longest_path(neighbor, visited, memo)
                    if sub_len + 1 > max_len:
                        max_len = sub_len + 1
                        max_path = [node] + sub_path
            memo[node] = (max_len, max_path)
            visited.remove(node)
            return max_len, max_path
        
        memo = {}
        critical_path = []
        max_len = 0
        for node in req_ids:
            _, path = longest_path(node, set(), memo)
            if len(path) > max_len:
                max_len = len(path)
                critical_path = path
        
        # Identify parallel groups (requirements with no dependencies)
        has_incoming = set()
        for rid, deps in graph.items():
            has_incoming.update(deps)
        parallel_groups = [[rid for rid in req_ids if rid not in has_incoming]]
        
        return {
            "graph": {rid: list(deps) for rid, deps in graph.items()},
            "critical_path": critical_path,
            "critical_path_length": max_len,
            "parallel_groups": parallel_groups,
            "total_dependencies": sum(len(deps) for deps in graph.values())
        }
    
    @classmethod
    def get_impacted_requirements(cls, requirement_id: str, graph: Dict) -> List[str]:
        """Get all requirements that depend (directly or indirectly) on given requirement"""
        impacted = set()
        stack = [requirement_id]
        while stack:
            node = stack.pop()
            for neighbor in graph.get(node, []):
                if neighbor not in impacted:
                    impacted.add(neighbor)
                    stack.append(neighbor)
        return list(impacted)
