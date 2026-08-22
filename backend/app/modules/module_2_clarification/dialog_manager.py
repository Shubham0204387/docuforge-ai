"""Manages multi-turn clarification dialog sessions"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class DialogManager:
    """Handles session state, question queue, and answer storage"""
    
    def __init__(self, session_id: str, project_id: int):
        self.session_id = session_id
        self.project_id = project_id
        self.questions = []
        self.answers = {}
        self.current_index = 0
        self.is_complete = False
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def from_session_data(cls, session_id: str, project_id: int, session_data: Dict):
        """Reconstruct dialog manager from stored session data"""
        manager = cls(session_id, project_id)
        manager.questions = session_data.get("questions", [])
        manager.answers = session_data.get("answers", {})
        manager.current_index = session_data.get("current_index", 0)
        manager.is_complete = session_data.get("is_complete", False)
        return manager
    
    def initialize(self, questions: List[Dict]):
        """Initialize dialog with questions"""
        self.questions = questions
        self.current_index = 0
        self.is_complete = False
        self.answers = {}
    
    def get_current_question(self) -> Optional[Dict]:
        """Get the next unanswered question"""
        if self.current_index < len(self.questions):
            question = self.questions[self.current_index]
            question["index"] = self.current_index
            question["total"] = len(self.questions)
            return question
        return None
    
    def submit_answer(self, answer: str) -> Dict:
        """Submit an answer and move to next question"""
        if self.current_index >= len(self.questions):
            return {"error": "No more questions", "is_complete": True}
        
        current_q = self.questions[self.current_index]
        self.answers[current_q["clarifies"]] = {
            "question": current_q["question"],
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.current_index += 1
        
        if self.current_index >= len(self.questions):
            self.is_complete = True
            return {
                "is_complete": True,
                "message": "Clarification complete",
                "answers_count": len(self.answers)
            }
        
        return {
            "is_complete": False,
            "next_question": self.get_current_question(),
            "progress": f"{self.current_index}/{len(self.questions)}"
        }
    
    def get_summary(self) -> Dict:
        """Get summary of all answers"""
        return {
            "total_questions": len(self.questions),
            "answered": len(self.answers),
            "answers": self.answers,
            "is_complete": self.is_complete
        }
    
    def to_session_data(self) -> Dict:
        """Convert to serializable format for database storage"""
        return {
            "questions": self.questions,
            "answers": self.answers,
            "current_index": self.current_index,
            "is_complete": self.is_complete,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def add_follow_up(self, follow_up_question: Dict):
        """Add a follow-up question at the current position"""
        self.questions.insert(self.current_index + 1, follow_up_question)
        self.updated_at = datetime.utcnow()
