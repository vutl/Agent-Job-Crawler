from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_

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
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/roles")
def list_roles():
    return ["AI Engineer", "ML Engineer", "MLOps Engineer", "Data Scientist"]

@app.get("/jobs")
@app.get("/api/v1/jobs")
def list_jobs(
    role: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    locked_only: bool = Query(False, description="Set True to query only paywalled/login-locked jobs"),
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Returns list of normalized jobs. Locked/Paywalled jobs are separated via locked_only flag."""
    query = db.query(Job).outerjoin(Company, Job.company_id == Company.id).outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)

    if locked_only:
        # Return ONLY actual paywalled / login-wall jobs (NOT non-technical jobs)
        query = query.filter(
            or_(
                Job.status == "paywall",
                Job.description_text.ilike("%PAYWALL_DETECTED%"),
                Job.description_text.ilike("%authentication required%"),
                Job.description_text.ilike("%paywall%"),
                Job.description_text.ilike("%sign in to continue%"),
            )
        )
    else:
        # Return ONLY clean, relevant, publicly accessible AI/ML engineering jobs
        query = query.filter(
            or_(JobAnalysis.is_relevant == True, JobAnalysis.job_id.is_(None)),
            Job.status != "paywall",
            ~Job.description_text.ilike("%PAYWALL_DETECTED%"),
            ~Job.description_text.ilike("%authentication required%"),
            ~Job.description_text.ilike("%paywall%"),
            ~Job.description_text.ilike("%sign in to continue%"),
        )

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
            "external_id": j.external_id,
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
def get_role_skills(role: str, top: int = 15, db: Session = Depends(get_db)):
    """Returns top demanded skills for a specific target role with required/preferred counts."""
    total_role_jobs = db.query(JobAnalysis).filter(JobAnalysis.role_family == role).count()
    if total_role_jobs == 0:
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
            func.sum(case((JobSkill.requirement_type == 'required', 1), else_=0)).label("required_count"),
            func.sum(case((JobSkill.requirement_type == 'preferred', 1), else_=0)).label("preferred_count"),
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .join(JobAnalysis, JobSkill.job_id == JobAnalysis.job_id)
        .filter(JobAnalysis.role_family == role)
        .group_by(Skill.id, Skill.canonical_name, Skill.category)
        .order_by(func.count(JobSkill.job_id).desc())
        .limit(top)
        .all()
    )

    skills_list = []
    for s in skill_counts:
        name, category, count, req_cnt, pref_cnt = s
        skills_list.append({
            "name": name,
            "category": category,
            "count": count,
            "share": round(count / total_role_jobs, 4) if total_role_jobs > 0 else 0,
            "required_count": req_cnt or 0,
            "preferred_count": pref_cnt or 0,
        })

    return {
        "role": role,
        "total_jobs": total_role_jobs,
        "skills": skills_list,
    }

@app.get("/system/data-freshness")
def data_freshness(db: Session = Depends(get_db)):
    """Returns system data freshness statistics."""
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    active_jobs = db.query(func.count(Job.id)).filter(Job.status == "active").scalar() or 0
    analyzed_jobs = db.query(func.count(JobAnalysis.job_id)).scalar() or 0
    latest_job = db.query(Job.last_seen_at).order_by(Job.last_seen_at.desc()).first()

    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "analyzed_jobs": analyzed_jobs,
        "latest_job_crawled_at": latest_job[0].isoformat() if latest_job and latest_job[0] else None,
    }

@app.get("/api/v1/intelligence/domains")
@app.get("/intelligence/domains")
def get_domain_intelligence():
    """Returns domain-specific engineering requirements and Capstone Project Blueprints."""
    from packages.domain_intelligence import DOMAIN_INTELLIGENCE_DATA
    return {
        "total_domains": len(DOMAIN_INTELLIGENCE_DATA),
        "domains": DOMAIN_INTELLIGENCE_DATA,
    }

