from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Схема для создания задачи [POST]
class TaskCreate(BaseModel):
    task_number: str = Field(..., max_length=20, description="Уникальный номер задачи")
    description: Optional[str] = Field(None, description="Полное описание задачи")
    deadline: Optional[datetime] = Field(None, description="Дедлайн выполнения")
    priority: Optional[str] = Field("medium", max_length=20, description="Приоритет")
    status: Optional[str] = Field("new", max_length=20, description="Статус задачи (new, in_progress, done)")

# Схема для обновления статуса задачи [PUT]
class TaskUpdate(BaseModel):
    task_number: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None)
    deadline: Optional[datetime] = Field(None)
    priority: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    