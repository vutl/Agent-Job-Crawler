from datetime import datetime
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from packages.database import Company, Job
from packages.schemas import NormalizedJobPost

def save_normalized_job(db: Session, post: NormalizedJobPost) -> Tuple[Job, bool]:
    """
    Upserts a normalized job posting into PostgreSQL.
    Deduplicates across different sources by canonical_url OR content_hash.
    Returns a tuple of (Job ORM model, is_new_or_changed: bool).
    """
    # 1. Get or create company
    company = db.query(Company).filter(Company.name == post.company_name).first()
    if not company:
        company = Company(
            name=post.company_name,
            domain=post.company_domain,
            careers_url=post.canonical_url,
        )
        db.add(company)
        db.flush()

    # 2. Check if job exists by canonical_url OR content_hash (Cross-source deduplication)
    existing_job = db.query(Job).filter(
        or_(Job.canonical_url == post.canonical_url, Job.content_hash == post.content_hash)
    ).first()

    now = datetime.utcnow()

    if existing_job:
        # Check if content has changed
        is_changed = existing_job.content_hash != post.content_hash
        existing_job.last_seen_at = now
        existing_job.status = "active"

        if is_changed:
            existing_job.title = post.title
            existing_job.location = post.location
            existing_job.description_raw = post.description_raw
            existing_job.description_text = post.description_text
            existing_job.content_hash = post.content_hash
            db.commit()
            db.refresh(existing_job)
            return existing_job, True
        else:
            db.commit()
            db.refresh(existing_job)
            return existing_job, False
    else:
        # Create new job
        new_job = Job(
            external_id=post.external_id,
            canonical_url=post.canonical_url,
            company_id=company.id,
            title=post.title,
            location=post.location,
            description_raw=post.description_raw,
            description_text=post.description_text,
            posted_at=post.posted_at or now,
            first_seen_at=now,
            last_seen_at=now,
            status="active",
            content_hash=post.content_hash,
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job, True
