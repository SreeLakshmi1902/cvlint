from pydantic import BaseModel, Field
from typing import Literal

class CompactRecommendation(BaseModel):
    priority: int
    action: str
    why: str
        
class CritiqueSummary(BaseModel):
    summary: str
    recommendations: list[CompactRecommendation] = Field(default_factory=list)
    
class Requirement(BaseModel):
    name: str
    alternatives: list[str] = Field(default_factory=list)
    category: Literal["technical", "domain", "soft_skill", "qualification", "experience"]
    importance: Literal["must_have", "nice_to_have"]
    min_years: float | None = None
    source_quote: str

class JobRequirements(BaseModel):
    job_title: str
    requirements: list[Requirement]
    
class RequirementVerdict(BaseModel):
    requirement_id: str
    verdict: Literal["met", "partial", "missing"]
    evidence_ids: list[str] = Field(default_factory=list)
    reason: str

class VerdictReport(BaseModel):
    verdicts: list[RequirementVerdict]