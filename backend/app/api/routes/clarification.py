"""API routes for clarification engine"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.app.database.connection import get_db
from backend.app.database.models import Project, ClarificationSession, User, Requirement
from backend.app.api.routes.auth import get_current_user
from backend.app.modules.module_2_clarification import (
    VagueTermDetector, QuestionGenerator, DialogManager, AssumptionLogger
)

router = APIRouter(prefix="/clarification", tags=["clarification"])

class AnswerRequest(BaseModel):
    answer: str

class StartRequest(BaseModel):
    requirement_text: str

@router.post("/start/{project_id}")
async def start_clarification(
    project_id: str,
    request: StartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new clarification session for a project"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if session already exists
    existing = db.query(ClarificationSession).filter(
        ClarificationSession.project_id == project.id
    ).first()
    if existing:
        # Return existing session status
        return {
            "session_exists": True,
            "project_id": project_id,
            "status": "in_progress",
            "message": "Clarification already in progress. Use /next to continue."
        }
    
    # Detect vague terms
    # Use the first requirement text or project raw input
    text_to_analyze = request.requirement_text or project.raw_input or ""
    vague_analysis = VagueTermDetector.detect(text_to_analyze, project.domain)
    
    # Generate questions
    questions = QuestionGenerator.generate_questions(
        text_to_analyze, 
        project.domain, 
        vague_analysis
    )
    
    # Create dialog manager
    import uuid
    session_id = str(uuid.uuid4())
    dialog = DialogManager(session_id, project.id)
    dialog.initialize(questions)
    
    # Create assumption logger
    assumption_logger = AssumptionLogger()
    
    # Log initial assumptions from vague term detection
    for vague in vague_analysis.get("suggestions", []):
        assumption_logger.log_assumption(
            original=vague["term"],
            clarified=vague["suggestion"],
            confidence=0.7,
            source="vague_term_detection"
        )
    
    # Save to database
    clarification_session = ClarificationSession(
        session_data=dialog.to_session_data(),
        assumptions=assumption_logger.to_list(),
        current_question_index=0,
        is_complete=False,
        project_id=project.id
    )
    db.add(clarification_session)
    db.commit()
    db.refresh(clarification_session)
    
    # Update project status
    project.status = "clarifying"
    db.commit()
    
    # Return first question
    first_question = dialog.get_current_question()
    return {
        "session_id": session_id,
        "project_id": project_id,
        "question": first_question,
        "vague_terms": vague_analysis["vague_terms"],
        "assumptions": assumption_logger.get_summary(),
        "progress": f"0/{len(questions)}"
    }

@router.get("/next/{project_id}")
async def get_next_question(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the next clarification question"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get clarification session
    session = db.query(ClarificationSession).filter(
        ClarificationSession.project_id == project.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="No clarification session found")
    
    # Reconstruct dialog manager
    dialog = DialogManager.from_session_data(
        str(session.id), 
        project.id, 
        session.session_data
    )
    
    question = dialog.get_current_question()
    if not question:
        return {
            "is_complete": True,
            "message": "Clarification complete",
            "answers": dialog.get_summary()
        }
    
    return {
        "is_complete": False,
        "question": question,
        "progress": f"{dialog.current_index}/{len(dialog.questions)}"
    }

@router.post("/answer/{project_id}")
async def submit_answer(
    project_id: str,
    answer_req: AnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an answer to the current question"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get clarification session
    session = db.query(ClarificationSession).filter(
        ClarificationSession.project_id == project.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="No clarification session found")
    
    # Reconstruct dialog manager
    dialog = DialogManager.from_session_data(
        str(session.id), 
        project.id, 
        session.session_data
    )
    
    # Submit answer
    result = dialog.submit_answer(answer_req.answer)
    
    # Check for follow-up questions
    if not result.get("is_complete"):
        from backend.app.modules.module_2_clarification.question_generator import QuestionGenerator
        follow_up = QuestionGenerator.generate_follow_up(
            answer_req.answer, 
            {"last_question": dialog.get_current_question()}
        )
        if follow_up:
            dialog.add_follow_up(follow_up)
    
    # Reconstruct assumption logger
    assumption_logger = AssumptionLogger.from_list(session.assumptions or [])
    
    # Update session in database
    session.session_data = dialog.to_session_data()
    session.assumptions = assumption_logger.to_list()
    session.current_question_index = dialog.current_index
    session.is_complete = dialog.is_complete
    db.commit()
    
    # If complete, update project status
    if dialog.is_complete:
        project.status = "complete"
        # Update requirements with clarified information
        # (This will be expanded in Phase 3)
        db.commit()
    
    return {
        "is_complete": result.get("is_complete", False),
        "next_question": result.get("next_question"),
        "progress": result.get("progress", f"{dialog.current_index}/{len(dialog.questions)}"),
        "answers_received": len(dialog.answers),
        "assumptions": assumption_logger.get_summary()
    }

@router.get("/status/{project_id}")
async def get_clarification_status(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current clarification status"""
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    session = db.query(ClarificationSession).filter(
        ClarificationSession.project_id == project.id
    ).first()
    if not session:
        return {"status": "not_started", "project_id": project_id}
    
    dialog = DialogManager.from_session_data(
        str(session.id), 
        project.id, 
        session.session_data
    )
    assumption_logger = AssumptionLogger.from_list(session.assumptions or [])
    
    return {
        "status": "in_progress" if not dialog.is_complete else "completed",
        "project_id": project_id,
        "progress": f"{dialog.current_index}/{len(dialog.questions)}",
        "answers_count": len(dialog.answers),
        "assumptions": assumption_logger.get_summary(),
        "is_complete": dialog.is_complete
    }
