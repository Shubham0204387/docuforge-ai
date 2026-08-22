"""Send notifications to Slack about project generation"""
import os
import requests
from typing import Dict

class SlackConnector:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
    
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send_notification(self, message: str, project_id: str = None) -> Dict:
        """Send a simple message to a Slack channel via webhook"""
        if not self.is_configured():
            return {"skipped": True, "message": "Slack webhook not configured"}
        
        payload = {"text": message}
        if project_id:
            payload["text"] = f"*DocuForge AI*\nProject `{project_id}`: {message}"
        
        try:
            resp = requests.post(self.webhook_url, json=payload)
            if resp.status_code == 200:
                return {"success": True}
            else:
                return {"error": resp.text, "status": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def notify_generation_complete(self, project_id: str, download_url: str = None) -> Dict:
        """Notify that project documentation has been generated"""
        msg = f"✅ Documentation generation complete for project *{project_id}*."
        if download_url:
            msg += f"\nDownload: {download_url}"
        return self.send_notification(msg, project_id)
