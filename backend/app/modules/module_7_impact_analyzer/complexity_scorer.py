"""Score requirement complexity on a 1-10 scale"""
import re
from typing import Dict, Any, List

class ComplexityScorer:
    """Evaluates technical complexity based on multiple factors"""
    
    # Weighted factors: each returns score 0-10, final = weighted sum / total_weight
    FACTORS = {
        "integration_points": {"weight": 3, "description": "Number of external systems/APIs"},
        "algorithmic_complexity": {"weight": 4, "description": "Complex logic, data structures"},
        "ui_complexity": {"weight": 2, "description": "Number of screens, interactions"},
        "data_complexity": {"weight": 3, "description": "Schema size, relationships, data volume"},
        "security_requirements": {"weight": 3, "description": "Encryption, auth, compliance"},
        "performance_constraints": {"weight": 2, "description": "Low latency, high throughput"},
        "concurrency": {"weight": 2, "description": "Concurrent users, race conditions"},
        "maintainability": {"weight": 1, "description": "Need for modularity, documentation"}
    }
    
    @classmethod
    def score(cls, requirement_text: str, category: str = None) -> Dict[str, Any]:
        """
        Compute complexity score for a requirement
        Returns: {"score": int 1-10, "factors": dict, "level": str}
        """
        text_lower = requirement_text.lower()
        factors_score = {}
        
        # 1. Integration points: count of words like api, webhook, third-party, service
        integration_keywords = ['api', 'webhook', 'third[- ]party', 'external', 'service', 'integration', 'soap', 'rest']
        integration_count = sum(1 for kw in integration_keywords if re.search(kw, text_lower))
        factors_score["integration_points"] = min(10, integration_count * 3)
        
        # 2. Algorithmic complexity: keywords: algorithm, optimize, calculate, compute, sort, search, pattern
        algo_keywords = ['algorithm', 'optimize', 'calculate', 'compute', 'sort', 'search', 'pattern', 'match', 'recommend', 'predict']
        algo_count = sum(1 for kw in algo_keywords if kw in text_lower)
        factors_score["algorithmic_complexity"] = min(10, algo_count * 2 + (2 if 'real-time' in text_lower else 0))
        
        # 3. UI complexity: number of forms, screens, dashboards, interactive elements
        ui_keywords = ['screen', 'form', 'dashboard', 'widget', 'dialog', 'modal', 'user interface', 'ui', 'frontend', 'page']
        ui_count = sum(1 for kw in ui_keywords if kw in text_lower)
        factors_score["ui_complexity"] = min(10, ui_count * 3)
        
        # 4. Data complexity: mentions of database, schema, data model, large volume
        data_keywords = ['database', 'schema', 'data model', 'table', 'relationship', 'index', 'query', 'store', 'retrieve']
        data_count = sum(1 for kw in data_keywords if kw in text_lower)
        factors_score["data_complexity"] = min(10, data_count * 2 + (3 if 'million' in text_lower or 'billion' in text_lower else 0))
        
        # 5. Security requirements
        sec_keywords = ['encrypt', 'decrypt', 'authenticate', 'authorize', 'pci', 'gdpr', 'hipaa', 'security', 'compliance']
        sec_count = sum(1 for kw in sec_keywords if kw in text_lower)
        factors_score["security_requirements"] = min(10, sec_count * 3)
        
        # 6. Performance constraints: response time, low latency, throughput
        perf_keywords = ['response time', 'latency', 'throughput', 'fast', 'within second', 'under', 'millisecond']
        perf_count = sum(1 for kw in perf_keywords if kw in text_lower)
        factors_score["performance_constraints"] = min(10, perf_count * 3)
        
        # 7. Concurrency: multi-user, concurrent, race condition, thread-safe
        conc_keywords = ['concurrent', 'multi-user', 'race condition', 'thread', 'parallel', 'simultaneous']
        conc_count = sum(1 for kw in conc_keywords if kw in text_lower)
        factors_score["concurrency"] = min(10, conc_count * 3)
        
        # 8. Maintainability: extensible, modular, documented, testable
        maint_keywords = ['modular', 'extensible', 'documented', 'testable', 'configurable', 'reusable']
        maint_count = sum(1 for kw in maint_keywords if kw in text_lower)
        factors_score["maintainability"] = min(10, maint_count * 3)
        
        # Weighted average
        total_weight = sum(cls.FACTORS[f]["weight"] for f in factors_score)
        weighted_sum = sum(factors_score[f] * cls.FACTORS[f]["weight"] for f in factors_score)
        final_score = round(weighted_sum / total_weight)
        final_score = max(1, min(10, final_score))  # clamp 1-10
        
        # Complexity level
        if final_score <= 3:
            level = "LOW"
        elif final_score <= 6:
            level = "MEDIUM"
        else:
            level = "HIGH"
        
        return {
            "score": final_score,
            "level": level,
            "factors": factors_score,
            "summary": f"Complexity {level} ({final_score}/10)"
        }
    
    @classmethod
    def batch_score(cls, requirements: List[Dict]) -> List[Dict]:
        """Score multiple requirements"""
        results = []
        for req in requirements:
            text = req.get('text', '')
            cat = req.get('category')
            result = cls.score(text, cat)
            results.append({
                "requirement_id": req.get('requirement_id'),
                "complexity": result
            })
        return results
