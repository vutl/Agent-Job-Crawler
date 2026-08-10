import logging
from datetime import datetime
from sqlalchemy.orm import Session
from packages.database import Job, Skill, JobSkill, JobAnalysis
from packages.schemas import AIJobExtractionResult, RoleFamily, SeniorityLevel
from .provider import LLMProvider
from .prefilter import is_prefilter_pass

logger = logging.getLogger(__name__)

async def extract_and_save_job(
    db: Session,
    job: Job,
    provider: LLMProvider,
    model_name: str = "ag/gemini-3.6-flash-high",
    prompt_version: str = "v1.0.0",
) -> JobAnalysis:
    """Runs fast pre-filter heuristics first (0 token), then LLM extraction if passed."""

    # 1. Tier 1: Fast Rule-Based Pre-Filter (< 1ms, 0 tokens)
    should_call_llm, prefilter_reason = is_prefilter_pass(job.title, job.description_text)

    if not should_call_llm:
        logger.info(f"Fast pre-filter rejected job '{job.title}': {prefilter_reason}")

        analysis = db.query(JobAnalysis).filter(JobAnalysis.job_id == job.id).first()
        if not analysis:
            analysis = JobAnalysis(
                job_id=job.id,
                role_family=RoleFamily.NOT_RELEVANT.value,
                seniority=SeniorityLevel.UNKNOWN.value,
                years_experience_min=0,
                education_requirement=None,
                is_relevant=False,
                relevance_reason=prefilter_reason,
                model="heuristic_prefilter",
                prompt_version=prompt_version,
                analyzed_at=datetime.utcnow(),
            )
            db.add(analysis)
        else:
            analysis.role_family = RoleFamily.NOT_RELEVANT.value
            analysis.seniority = SeniorityLevel.UNKNOWN.value
            analysis.is_relevant = False
            analysis.relevance_reason = prefilter_reason
            analysis.model = "heuristic_prefilter"
            analysis.analyzed_at = datetime.utcnow()

        db.query(JobSkill).filter(JobSkill.job_id == job.id).delete()
        db.commit()
        db.refresh(analysis)
        return analysis

    # 2. Tier 2: Call LLM Provider for Deep Extraction
    result: AIJobExtractionResult = await provider.extract_job_info(job.title, job.description_text)

    is_job_relevant = (
        result.is_relevant and
        result.is_technical_ai_role and
        result.role_family != RoleFamily.NOT_RELEVANT
    )

    analysis = db.query(JobAnalysis).filter(JobAnalysis.job_id == job.id).first()
    if not analysis:
        analysis = JobAnalysis(
            job_id=job.id,
            role_family=result.role_family.value,
            seniority=result.seniority.value,
            years_experience_min=result.years_experience_min,
            education_requirement=result.education_requirement,
            is_relevant=is_job_relevant,
            relevance_reason=result.relevance_reason,
            model=model_name,
            prompt_version=prompt_version,
            analyzed_at=datetime.utcnow(),
        )
        db.add(analysis)
    else:
        analysis.role_family = result.role_family.value
        analysis.seniority = result.seniority.value
        analysis.years_experience_min = result.years_experience_min
        analysis.education_requirement = result.education_requirement
        analysis.is_relevant = is_job_relevant
        analysis.relevance_reason = result.relevance_reason
        analysis.model = model_name
        analysis.prompt_version = prompt_version
        analysis.analyzed_at = datetime.utcnow()

    db.query(JobSkill).filter(JobSkill.job_id == job.id).delete()

    if is_job_relevant:
        for skill_item in result.skills:
            skill = db.query(Skill).filter(Skill.canonical_name == skill_item.name).first()
            if not skill:
                skill = Skill(
                    canonical_name=skill_item.name,
                    category=skill_item.category.value,
                    aliases=[skill_item.name],
                )
                db.add(skill)
                db.flush()

            job_skill = JobSkill(
                job_id=job.id,
                skill_id=skill.id,
                evidence_text=skill_item.evidence,
                requirement_type=skill_item.requirement_type.value,
                confidence=skill_item.confidence,
                extractor_version=prompt_version,
            )
            db.add(job_skill)
    else:
        logger.info(f"Skipped skill extraction for non-relevant job: '{job.title}' (Reason: {result.relevance_reason})")

    db.commit()
    db.refresh(analysis)
    return analysis
