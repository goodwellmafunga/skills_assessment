from pydantic import BaseModel, Field


class AnswerInput(BaseModel):
    question_id: int
    option_id: int


class AssessmentSubmitRequest(BaseModel):
    submission_token: str = Field(min_length=8, max_length=64)
    respondent_sector: str | None = None
    respondent_category: str | None = None
    answers: list[AnswerInput]


class RecommendationOut(BaseModel):
    skill_area: str
    priority: str
    message: str


class AssessmentResultOut(BaseModel):
    assessment_id: int
    overall_score: float
    soft_score: float
    digital_score: float
    recommendations: list[RecommendationOut]
