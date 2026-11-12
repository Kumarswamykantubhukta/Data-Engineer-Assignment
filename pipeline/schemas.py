
from typing import Optional
from pydantic import BaseModel, Field


class ExtractedJob(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    work_arrangement: Optional[str] = None
    employment_type: Optional[str] = None
    experience_required: Optional[str] = None
    salary: Optional[str] = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    # Evidence supporting extracted information
    evidence: dict[str, Optional[str]] = Field(default_factory=dict)
