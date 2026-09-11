from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import FocusSession, Task
from app.schemas import FocusSessionCreate, FocusSessionRead


def create_focus_session(db: Session, session_in: FocusSessionCreate) -> FocusSessionRead:
    start_time = session_in.start_time or datetime.now(timezone.utc)
    end_time = session_in.end_time or datetime.now(timezone.utc)

    # Calculate actual duration if not provided
    actual_duration = session_in.actual_duration_minutes
    if actual_duration <= 0 and end_time and start_time:
        actual_duration = round((end_time - start_time).total_seconds() / 60.0, 2)

    session = FocusSession(
        task_id=session_in.task_id,
        start_time=start_time,
        end_time=end_time,
        planned_duration_minutes=session_in.planned_duration_minutes,
        actual_duration_minutes=max(0.0, actual_duration),
        status=session_in.status or "completed",
        notes=session_in.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    task_title = None
    if session.task_id:
        task = db.query(Task).filter(Task.id == session.task_id).first()
        if task:
            task_title = task.title

    return FocusSessionRead(
        id=session.id,
        task_id=session.task_id,
        task_title=task_title,
        planned_duration_minutes=session.planned_duration_minutes,
        actual_duration_minutes=session.actual_duration_minutes,
        status=session.status,
        notes=session.notes,
        start_time=session.start_time,
        end_time=session.end_time,
        created_at=session.created_at,
    )


def get_focus_sessions(
    db: Session,
    limit: int = 50,
    task_id: Optional[int] = None,
) -> List[FocusSessionRead]:
    query = db.query(FocusSession, Task.title).outerjoin(Task, FocusSession.task_id == Task.id)
    if task_id:
        query = query.filter(FocusSession.task_id == task_id)

    results = query.order_by(desc(FocusSession.start_time)).limit(limit).all()
    sessions = []
    for session, task_title in results:
        sessions.append(
            FocusSessionRead(
                id=session.id,
                task_id=session.task_id,
                task_title=task_title,
                planned_duration_minutes=session.planned_duration_minutes,
                actual_duration_minutes=session.actual_duration_minutes,
                status=session.status,
                notes=session.notes,
                start_time=session.start_time,
                end_time=session.end_time,
                created_at=session.created_at,
            )
        )
    return sessions
