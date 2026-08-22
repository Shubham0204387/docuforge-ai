"""Jira integration – create project, epics, stories from requirements"""
import os
import requests
from typing import List, Dict, Any
import json

class JiraConnector:
    def __init__(self, settings=None):
        if settings:
            self.base_url = settings.jira_base_url or os.getenv("JIRA_BASE_URL", "")
            self.email = settings.jira_email or os.getenv("JIRA_EMAIL", "")
            self.api_token = settings.jira_api_token or os.getenv("JIRA_API_TOKEN", "")
        else:
            self.base_url = os.getenv("JIRA_BASE_URL", "")
            self.email = os.getenv("JIRA_EMAIL", "")
            self.api_token = os.getenv("JIRA_API_TOKEN", "")
        self.project_key = None
        
    def is_configured(self) -> bool:
        return bool(self.base_url and self.email and self.api_token)
    
    def create_project(self, name: str, key: str) -> Dict:
        """Create a new Jira project (simplified – uses company-managed template)"""
        if not self.is_configured():
            return {"error": "Jira not configured", "skipped": True}
        
        url = f"{self.base_url}/rest/api/3/project"
        auth = (self.email, self.api_token)
        payload = {
            "key": key.upper(),
            "name": name,
            "projectTypeKey": "software",
            "templateId": 10000  # basic software development template
        }
        try:
            resp = requests.post(url, json=payload, auth=auth)
            if resp.status_code == 201:
                self.project_key = key.upper()
                return resp.json()
            else:
                return {"error": resp.text, "status": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def create_epic(self, summary: str, description: str = "") -> Dict:
        """Create an epic in the project"""
        if not self.project_key:
            return {"error": "No project key set"}
        url = f"{self.base_url}/rest/api/3/issue"
        auth = (self.email, self.api_token)
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Epic"}
            }
        }
        try:
            resp = requests.post(url, json=payload, auth=auth)
            return resp.json() if resp.status_code == 201 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}
    
    def create_story(self, summary: str, description: str = "", epic_link: str = None) -> Dict:
        """Create a story/task in the project"""
        if not self.project_key:
            return {"error": "No project key set"}
        url = f"{self.base_url}/rest/api/3/issue"
        auth = (self.email, self.api_token)
        fields = {
            "project": {"key": self.project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Task"}
        }
        if epic_link:
            fields["customfield_10014"] = epic_link  # common epic link field
        payload = {"fields": fields}
        try:
            resp = requests.post(url, json=payload, auth=auth)
            return resp.json() if resp.status_code == 201 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}
    
    def push_requirements(self, requirements: List[Dict], project_name: str) -> Dict:
        """Create one epic per category and stories per requirement"""
        if not self.is_configured():
            return {"skipped": True, "message": "Jira credentials missing"}
        # Create project
        proj_key = project_name.replace(" ", "")[:10]
        self.create_project(project_name, proj_key)
        if not self.project_key:
            return {"error": "Could not create Jira project"}
        
        # Group requirements by category
        categories = {}
        for req in requirements:
            cat = req.get('category', 'General')
            categories.setdefault(cat, []).append(req)
        
        epic_map = {}
        created_issues = 0
        for cat, reqs in categories.items():
            epic = self.create_epic(cat, f"Epic for {cat} requirements")
            epic_id = epic.get('key')
            if epic_id:
                epic_map[cat] = epic_id
            for req in reqs:
                story = self.create_story(
                    summary=req.get('requirement_id', '') + ": " + req.get('text', '')[:80],
                    description=req.get('text', ''),
                    epic_link=epic_id
                )
                if story.get('key'):
                    created_issues += 1
        return {"created_issues": created_issues, "project_key": self.project_key}
