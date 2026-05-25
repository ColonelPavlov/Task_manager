from pydantic import BaseModel

# Схема для создания задачи
class TaskCreate(BaseModel):
    title: str
    description: str | None = None

# Схема для обновления статуса задачи
class TaskUpdate(BaseModel):
    status: str
