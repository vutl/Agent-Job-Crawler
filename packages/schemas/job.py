from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class RoleFamily(str, Enum):
    AI_ENGINEER = "AI Engineer"
    ML_ENGINEER = "ML Engineer"
    MLOPS_ENGINEER = "MLOps Engineer"
    DATA_SCIENTIST = "Data Scientist"
    BACKEND_ENGINEER = "Backend Engineer"
    PLATFORM_ENGINEER = "Platform Engineer"
    NOT_RELEVANT = "Not Relevant / Non-Technical"

class SeniorityLevel(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    UNKNOWN = "unknown"

class RequirementType(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    MENTIONED = "mentioned"

class SkillCategory(str, Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    CLOUD = "cloud"
    DEVOPS = "devops"
    DATABASE = "database"
    ML_FRAMEWORK = "ml_framework"
    OTHER = "other"

class ExtractedSkill(BaseModel):
    name: str = Field(..., description="Canonical name of the skill, e.g. 'PyTorch', 'Kubernetes'")
    category: SkillCategory = Field(SkillCategory.OTHER, description="Category of the technology")
    requirement_type: RequirementType = Field(RequirementType.REQUIRED, description="Whether required or preferred")
    evidence: str = Field(..., description="Exact text snippet supporting this skill requirement")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score between 0 and 1")

class AIJobExtractionResult(BaseModel):
    is_technical_ai_role: bool = Field(
        True,
        description="True if this is a genuine software engineering, data science, ML, or platform engineering role. Set to False for non-technical roles like AI Content Creator, Video AI Editor, AI Copywriter, Marketing, etc."
    )
    is_relevant: bool = Field(
        True,
        description="True if the actual job description text relates to building, deploying, or using AI/ML/Data technologies or software engineering. Set to False if completely unrelated."
    )
    relevance_reason: Optional[str] = Field(
        default=None,
        description="Brief 1-sentence reason explaining why this job is relevant or irrelevant based on full description text."
    )
    role_family: RoleFamily
    seniority: SeniorityLevel
    years_experience_min: Optional[int] = Field(default=None, description="Minimum required years of experience")
    education_requirement: Optional[str] = Field(default=None, description="Minimum education requirement")
    skills: List[ExtractedSkill] = Field(default_factory=list)

class NormalizedJobPost(BaseModel):
    external_id: Optional[str] = None
    canonical_url: str
    company_name: str
    company_domain: Optional[str] = None
    title: str
    location: Optional[str] = None
    description_raw: str
    description_text: str
    posted_at: Optional[datetime] = None
    content_hash: str
