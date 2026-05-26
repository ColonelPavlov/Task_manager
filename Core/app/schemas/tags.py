from pydantic import BaseModel, Field

class TagCreate(BaseModel):
    name: str = Field(..., max_length=50, description="Название тега")
    color: str = Field("#4a6741", max_length=7, description="Цвет тега в формате HEX (например, #FFFFFF)")
