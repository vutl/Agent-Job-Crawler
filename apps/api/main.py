from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from packages.database import get_db, Job, JobAnalysis, JobSkill, Skill, Company

app = FastAPI(
    title="AI Job Intelligence API",
    description="Market demand intelligence and skill analytics for tech roles",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-job-intelligence-api",
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    results = (
        db.query(JobAnalysis.role_family, func.count(JobAnalysis.id))
        .group_by(JobAnalysis.role_family)
        .all()
    )
    return [{"role": r[0], "count": r[1]} for r in results]

@app.get("/jobs")
@app.get("/api/v1/jobs")
def list_jobs(
    role: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Returns list of normalized jobs with extracted skills, role analysis, and outbound apply link."""
    query = db.query(Job).outerjoin(Company, Job.company_id == Company.id)

    if source:
        query = query.filter(Job.canonical_url.ilike(f"%{source}%"))

    if search:
        query = query.filter((Job.title.ilike(f"%{search}%")) | (Company.name.ilike(f"%{search}%")))

    total = query.count()
    jobs = query.order_by(Job.id.desc()).offset(offset).limit(limit).all()

    items = []
    for j in jobs:
        analysis = db.query(JobAnalysis).filter(JobAnalysis.job_id == j.id).first()
        job_skills = (
            db.query(Skill.canonical_name, JobSkill.requirement_type)
            .join(JobSkill, Skill.id == JobSkill.skill_id)
            .filter(JobSkill.job_id == j.id)
            .all()
        )

        company_name = j.company.name if j.company else "Unknown Company"
        company_domain = j.company.domain if j.company else ""

        items.append({
            "id": j.id,
            "title": j.title,
            "company_name": company_name,
            "company_domain": company_domain,
            "canonical_url": j.canonical_url,
            "location": j.location,
            "description_text": j.description_text,
            "posted_at": j.posted_at.isoformat() if j.posted_at else None,
            "last_seen_at": j.last_seen_at.isoformat() if j.last_seen_at else None,
            "status": j.status,
            "role_family": analysis.role_family if analysis else "Unclassified",
            "seniority": analysis.seniority if analysis else "Mid",
            "is_relevant": analysis.is_relevant if analysis else True,
            "relevance_reason": analysis.relevance_reason if analysis else None,
            "skills": [{"name": s[0], "requirement_type": s[1]} for s in job_skills],
        })

    return {
        "total": total,
        "items": items,
    }

@app.get("/jobs/{job_id}")
@app.get("/api/v1/jobs/{job_id}")
def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    j = db.query(Job).filter(Job.id == job_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Job posting not found")

    analysis = db.query(JobAnalysis).filter(JobAnalysis.job_id == j.id).first()
    job_skills = (
        db.query(Skill.canonical_name, Skill.category, JobSkill.requirement_type, JobSkill.evidence_text)
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .filter(JobSkill.job_id == j.id)
        .all()
    )

    company_name = j.company.name if j.company else "Unknown Company"
    company_domain = j.company.domain if j.company else ""

    return {
        "id": j.id,
        "title": j.title,
        "company_name": company_name,
        "company_domain": company_domain,
        "canonical_url": j.canonical_url,
        "location": j.location,
        "description_raw": j.description_raw,
        "description_text": j.description_text,
        "posted_at": j.posted_at.isoformat() if j.posted_at else None,
        "last_seen_at": j.last_seen_at.isoformat() if j.last_seen_at else None,
        "status": j.status,
        "role_family": analysis.role_family if analysis else "Unclassified",
        "seniority": analysis.seniority if analysis else "Mid",
        "is_relevant": analysis.is_relevant if analysis else True,
        "relevance_reason": analysis.relevance_reason if analysis else None,
        "skills": [
            {
                "name": s[0],
                "category": s[1],
                "requirement_type": s[2],
                "evidence_text": s[3],
            }
            for s in job_skills
        ],
    }

@app.get("/roles/{role}/skills")
def get_role_skills(
    role: str,
    top: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total_jobs = (
        db.query(func.count(JobAnalysis.id))
        .filter(JobAnalysis.role_family == role)
        .scalar()
        or 0
    )

    if total_jobs == 0:
        return {
            "role": role,
            "total_jobs": 0,
            "skills": [],
        }

    skill_counts = (
        db.query(
            Skill.canonical_name,
            Skill.category,
            func.count(JobSkill.job_id).label("job_count"),
            func.sum(func.case((JobSkill.requirement_type == 'required', 1), else_=0)).label("required_count"),
            func.sum(func.case((JobSkill.requirement_type == 'preferred', 1), else_=0)).label("preferred_count"),
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .join(JobAnalysis, JobSkill.job_id == JobAnalysis.job_id)
        .filter(JobAnalysis.role_family == role)
        .group_by(Skill.id, Skill.canonical_name, Skill.category)
        .order_by(func.count(JobSkill.job_id).desc())
        .limit(top)
        .all()
    )

    skills_data = []
    for sc in skill_counts:
        skills_data.append({
            "name": sc.canonical_name,
            "category": sc.category,
            "count": sc.job_count,
            "share": round(sc.job_count / total_jobs, 4),
            "required_count": sc.required_count or 0,
            "preferred_count": sc.preferred_count or 0,
        })

    return {
        "role": role,
        "total_jobs": total_jobs,
        "skills": skills_data,
    }

@app.get("/system/data-freshness")
def data_freshness(db: Session = Depends(get_db)):
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    active_jobs = db.query(func.count(Job.id)).filter(Job.status == "active").scalar() or 0
    analyzed_jobs = db.query(func.count(JobAnalysis.id)).scalar() or 0
    latest_job = db.query(func.max(Job.last_seen_at)).scalar()

    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "analyzed_jobs": analyzed_jobs,
        "latest_job_crawled_at": latest_job.isoformat() if latest_job else None,
    }
