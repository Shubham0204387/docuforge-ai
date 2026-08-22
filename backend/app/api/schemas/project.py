from pydantic import BaseModel

class ProjectInput(BaseModel):
    text: str
