import json
import os
from typing import Dict, Any, List, Optional

class KnowledgeBaseLoader:
    _instance = None
    _cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all()
        return cls._instance
    
    def _load_all(self):
        # Get absolute path to knowledge_base folder
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../knowledge_base'))
        print(f"Loading knowledge base from: {base_path}")  # Debug
        
        self.domains = {}
        domains_path = os.path.join(base_path, 'domains')
        if os.path.exists(domains_path):
            for domain_dir in os.listdir(domains_path):
                domain_path = os.path.join(domains_path, domain_dir)
                req_file = os.path.join(domain_path, 'requirements.json')
                if os.path.exists(req_file):
                    with open(req_file, 'r') as f:
                        self.domains[domain_dir] = json.load(f)
                        print(f"Loaded domain: {domain_dir}")
        
        self.rules = []
        rules_path = os.path.join(base_path, 'inference_rules', 'rules.json')
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                data = json.load(f)
                self.rules = data.get('rules', [])
                print(f"Loaded {len(self.rules)} rules")
        else:
            print(f"Rules file not found at {rules_path}")
        
        self.compliance = {}
        compliance_path = os.path.join(base_path, 'compliance')
        if os.path.exists(compliance_path):
            for comp_file in os.listdir(compliance_path):
                if comp_file.endswith('.json'):
                    with open(os.path.join(compliance_path, comp_file), 'r') as f:
                        key = comp_file.replace('.json', '')
                        self.compliance[key] = json.load(f)
    
    def get_domain_requirements(self, domain: str) -> List[Dict]:
        if domain in self.domains:
            return self.domains[domain].get('mandatory_requirements', [])
        return []
    
    def get_domain_patterns(self, domain: str) -> List[Dict]:
        if domain in self.domains:
            return self.domains[domain].get('common_patterns', [])
        return []
    
    def get_rules(self, domain: str = None) -> List[Dict]:
        if domain:
            return [r for r in self.rules if r.get('domain') == domain or r.get('domain') == 'general']
        return self.rules
    
    def get_compliance(self, name: str) -> Optional[Dict]:
        return self.compliance.get(name.lower())
    
    def reload(self):
        self._load_all()
