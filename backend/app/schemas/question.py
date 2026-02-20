from pydantic import BaseModel, Field


class QuestionOptionIn(BaseModel):
    label: str = Field(max_length=10)
    text: str
    score: int = Field(ge=1, le=5)


class QuestionCreate(BaseModel):
    text: str
    domain: str = Field(pattern="^(soft|digital)$")
    category: str
    display_order: int = 0
    is_active: bool = True
    options: list[QuestionOptionIn]


class QuestionOptionOut(BaseModel):
    id: int
    label: str
    text: str
    score: int

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    id: int
    text: str
    domain: str
    category: str
    display_order: int
    is_active: bool
    options: list[QuestionOptionOut]

    class Config:
        from_attributes = True
