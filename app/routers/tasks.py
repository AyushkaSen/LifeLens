from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TaskCreate, TaskUpdate, TaskRead
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_new_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    return task_service.create_task(db, task_in)


@router.get("", response_model=List[TaskRead])
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed, all"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    return task_service.get_tasks(db, status=status, category=category)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    updated = task_service.update_task(db, task_id, task_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.patch("/{task_id}/toggle", response_model=TaskRead)
def toggle_task_status(task_id: int, db: Session = Depends(get_db)):
    toggled = task_service.toggle_task(db, task_id)
    if not toggled:
        raise HTTPException(status_code=404, detail="Task not found")
    return toggled


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = task_service.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully", "id": task_id}
