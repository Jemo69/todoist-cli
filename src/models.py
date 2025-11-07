from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import date, datetime


class TaskDue(BaseModel):
    date: str  # Represents the date part, e.g., "2025-10-11"
    string: str
    lang: str
    is_recurring: bool


class Task(BaseModel):
    id : str | None = None 
    content: str
    description: str
    project_id:  str | None = None
    priority: int


class TaskUpdate(BaseModel):
    content: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None


class TodoistModel(BaseModel):
    id: str
    assigner_id: Optional[str] = Field(None, alias="assigned_by_uid")
    assignee_id: Optional[str] = Field(None, alias="responsible_uid")
    project_id: str
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    order: int = Field(..., alias="child_order")
    content: str
    description: str
    is_completed: bool = Field(..., alias="checked")
    labels: list[str]
    priority: int
    comment_count: int = Field(..., alias="note_count")
    creator_id: str = Field(..., alias="added_by_uid")
    created_at: datetime = Field(..., alias="added_at")
    due: Optional[TaskDue]
    url: Optional[str] = None
    duration: Optional[Any]
    deadline: Optional[Any]
