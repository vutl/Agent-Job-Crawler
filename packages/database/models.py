import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    careers_url = Column(Text, nullable=True)
    ats_type = Column(String(50), nullable=True)  # e.g. greenhouse, lever, workday
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job_sources = relationship("JobSource", back_populates="company", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="company")

class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    source_type = Column(String(50), nullable=False)  # e.g. ats_api, html_scrape
    source_url = Column(Text, nullable=False)
    crawl_strategy = Column(String(50), nullable=False)  # e.g. greenhouse_api, lever_api, dom
    last_crawled_at = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)

    company = relationship("Company", back_populates="job_sources")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    external_id = Column(String(255), nullable=True)
    canonical_url = Column(Text, unique=True, nullable=False, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    description_raw = Column(Text, nullable=False)
    description_text = Column(Text, nullable=False)
    posted_at = Column(DateTime, nullable=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="active")  # active, removed
    content_hash = Column(String(64), nullable=False, index=True)

    company = relationship("Company", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    analysis = relationship("JobAnalysis", back_populates="job", uselist=False, cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    canonical_name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, default="other")  # language, framework, devops, etc.
    aliases = Column(JSON, default=list)

    job_skills = relationship("JobSkill", back_populates="skill")

class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False, index=True)
    evidence_text = Column(Text, nullable=False)
    requirement_type = Column(String(50), default="required")  # required, preferred, mentioned
    confidence = Column(Float, default=1.0)
    extractor_version = Column(String(50), nullable=False, default="v1.0.0")

    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="job_skills")

    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )

class JobAnalysis(Base):
    __tablename__ = "job_analysis"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id"), unique=True, nullable=False)
    role_family = Column(String(100), nullable=False, index=True)
    seniority = Column(String(50), nullable=False, default="unknown")
    years_experience_min = Column(Integer, nullable=True)
    education_requirement = Column(String(255), nullable=True)
    is_relevant = Column(Boolean, default=True, index=True)
    relevance_reason = Column(Text, nullable=True)
    model = Column(String(100), nullable=False)
    prompt_version = Column(String(50), nullable=False, default="v1.0.0")
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="analysis")

class SkillSnapshot(Base):
    __tablename__ = "skill_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    snapshot_date = Column(Date, nullable=False, index=True)
    role_family = Column(String(100), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    job_count = Column(Integer, nullable=False, default=0)
    role_job_count = Column(Integer, nullable=False, default=0)
    share = Column(Float, nullable=False, default=0.0)

    skill = relationship("Skill")
