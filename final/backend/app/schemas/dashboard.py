from pydantic import BaseModel

class GapItem(BaseModel):
    skill_area: str
    avg_score: float
    n_answers: int = 0

class DashboardSummary(BaseModel):
    total_assessments: int
    avg_overall: float
    avg_soft: float
    avg_digital: float
    top_gaps: list[GapItem]