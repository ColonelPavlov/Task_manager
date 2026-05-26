from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=100, description="Название нового проекта")
