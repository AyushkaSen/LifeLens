from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


def create_task(db: Session, task_in: TaskCreate) -> Task:
    task = Task(
        title=task_in.title.strip(),
        category=task_in.category.strip() if task_in.category else "Work",
        priority=task_in.priority.strip() if task_in.priority else "Medium",
        deadline=task_in.deadline,
        estimated_duration_minutes=task_in.estimated_duration_minutes,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(
    db: Session,
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
) -> List[Task]:
    query = db.query(Task)
    if status and status.lower() != "all":
        query = query.filter(Task.status == status.lower())
    if category and category.lower() != "all":
        query = query.filter(Task.category.ilike(category))
    return query.order_by(desc(Task.created_at)).limit(limit).all()


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Optional[Task]:
    task = get_task_by_id(db, task_id)
    if not task:
        return None

    update_data = task_in.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == "completed" and not task.completed_at:
        task.completed_at = datetime.now(timezone.utc)
    elif "status" in update_data and update_data["status"] != "completed":
        task.completed_at = None

    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


def toggle_task(db: Session, task_id: int) -> Optional[Task]:
    task = get_task_by_id(db, task_id)
    if not task:
        return None

    if task.status == "completed":
        task.status = "pending"
        task.completed_at = None
    else:
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)

    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = get_task_by_id(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True
