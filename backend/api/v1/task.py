from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from backend.db.models import Task
from backend.db.database import get_session
from backend.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead)
def create_task(data: TaskCreate, session: Session = Depends(get_session)):
    task = Task(**data.dict())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/", response_model=list[TaskRead])
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: UUID, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: UUID, data: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
