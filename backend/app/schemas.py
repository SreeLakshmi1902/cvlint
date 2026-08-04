from pydantic import BaseModel
from typing import List


class ResumeCritique(BaseModel):
    overall_score: int
    strengths: List[str]
    missing_skills: List[str]
    ats_issues: List[str]
    recommendations: List[str]