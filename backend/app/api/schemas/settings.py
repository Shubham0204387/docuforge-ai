from pydantic import BaseModel
from typing import Optional

class UserSettingsSchema(BaseModel):
    jira_base_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    github_token: Optional[str] = None
    github_username: Optional[str] = None
    slack_webhook_url: Optional[str] = None

    class Config:
        from_attributes = True
