"""Detects circular dependencies and priority deadlocks"""
from typing import List, Dict, Set, Tuple

class PriorityDeadlockFinder:
    """Finds dependency cycles that block prioritization"""
    
    @classmethod
    def find_deadlocks(cls, requirements: List[Dict]) -> List[Dict]:
        """
        Detect circular dependencies among requirements
        Returns list of deadlock cycles
        """
        # Build dependency graph
        graph = {}
        req_map = {req.get('requirement_id', f"REQ_{i}"): req for i, req in enumerate(requirements)}
        
        for req in requirements:
            req_id = req.get('requirement_id', '')
            deps = req.get('dependencies', [])
            graph[req_id] = deps
        
        # Find cycles using DFS
        cycles = cls._find_cycles(graph)
        
        deadlocks = []
        for cycle in cycles:
            if len(cycle) > 1:
                # Check if cycle creates a priority deadlock
                deadlocks.append({
                    "type": "priority_deadlock",
                    "requirements_involved": cycle,
                    "description": f"Circular dependency detected: {' -> '.join(cycle)}",
                    "severity": "CRITICAL",
                    "details": {"cycle": cycle}
                })
        
        return deadlocks
    
    @classmethod
    def _find_cycles(cls, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find all cycles in directed graph using DFS"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found cycle
                start_idx = path.index(node)
                cycles.append(path[start_idx:] + [node])
                return
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor, path)
            
            rec_stack.remove(node)
            path.pop()
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    @classmethod
    def suggest_resolution(cls, cycle: List[str]) -> str:
        """Suggest how to break a dependency cycle"""
        if len(cycle) <= 1:
            return "No cycle detected"
        
        # Suggest breaking the weakest link
        return f"Break the cycle by removing or redefining dependency between '{cycle[0]}' and '{cycle[1]}'. Consider merging requirements or introducing an intermediate requirement."
