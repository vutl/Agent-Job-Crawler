from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from packages.database import get_db, Job, JobAnalysis, JobSkill, Skill

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

@app.get("/roles/{role}/skills")
def get_role_skills(
    role: str,
    top: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # Total jobs analyzed for role
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

    # Query skills count for this role
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
