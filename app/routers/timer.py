from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FocusSessionCreate, FocusSessionRead
from app.services import timer_service

router = APIRouter(prefix="/api/timer", tags=["Focus Timer"])


@router.post("/sessions", response_model=FocusSessionRead, status_code=status.HTTP_201_CREATED)
def record_focus_session(session_in: FocusSessionCreate, db: Session = Depends(get_db)):
    return timer_service.create_focus_session(db, session_in)


@router.get("/sessions", response_model=List[FocusSessionRead])
def list_focus_sessions(
    limit: int = Query(50, ge=1, le=200),
    task_id: Optional[int] = Query(None, description="Filter sessions by task ID"),
    db: Session = Depends(get_db),
):
    return timer_service.get_focus_sessions(db, limit=limit, task_id=task_id)
