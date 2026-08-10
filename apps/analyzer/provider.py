import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from packages.schemas import (
    AIJobExtractionResult,
    RoleFamily,
    SeniorityLevel,
    ExtractedSkill,
    SkillCategory,
    RequirementType,
)

logger = logging.getLogger(__name__)

def clean_json_codeblock(text: str) -> str:
    """Strips markdown ```json ... ``` codeblocks from LLM string output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def extract_job_info(self, title: str, description_text: str) -> AIJobExtractionResult:
        """Extracts structured role, seniority, and skills from a job posting."""
        pass

class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for deterministic testing without external API calls."""

    async def extract_job_info(self, title: str, description_text: str) -> AIJobExtractionResult:
        title_lower = title.lower()

        # Check for non-technical AI roles
        non_tech_keywords = ["editor", "content creator", "copywriter", "marketing", "video generator", "prompt writer"]
        if any(kw in title_lower for kw in non_tech_keywords):
            return AIJobExtractionResult(
                is_technical_ai_role=False,
                is_relevant=False,
                relevance_reason="Job title indicates non-technical content creation/marketing role.",
                role_family=RoleFamily.NOT_RELEVANT,
                seniority=SeniorityLevel.UNKNOWN,
                years_experience_min=0,
                education_requirement=None,
                skills=[],
            )

        if "mlops" in title_lower:
            role = RoleFamily.MLOPS_ENGINEER
        elif "ml" in title_lower or "machine learning" in title_lower:
            role = RoleFamily.ML_ENGINEER
        elif "data scientist" in title_lower:
            role = RoleFamily.DATA_SCIENTIST
        else:
            role = RoleFamily.AI_ENGINEER

        seniority = SeniorityLevel.SENIOR if "senior" in title_lower else SeniorityLevel.MID

        skills = []
        desc_lower = description_text.lower()

        keywords = [
            ("python", "Python", SkillCategory.LANGUAGE),
            ("pytorch", "PyTorch", SkillCategory.ML_FRAMEWORK),
            ("tensorflow", "TensorFlow", SkillCategory.ML_FRAMEWORK),
            ("kubernetes", "Kubernetes", SkillCategory.DEVOPS),
            ("docker", "Docker", SkillCategory.DEVOPS),
            ("aws", "AWS", SkillCategory.CLOUD),
            ("gcp", "GCP", SkillCategory.CLOUD),
            ("fastapi", "FastAPI", SkillCategory.FRAMEWORK),
            ("postgresql", "PostgreSQL", SkillCategory.DATABASE),
            ("langchain", "LangChain", SkillCategory.ML_FRAMEWORK),
        ]

        for kw, canonical, cat in keywords:
            if kw in desc_lower:
                skills.append(
                    ExtractedSkill(
                        name=canonical,
                        category=cat,
                        requirement_type=RequirementType.REQUIRED,
                        evidence=f"Mentioned {canonical} in description",
                        confidence=0.95,
                    )
                )

        return AIJobExtractionResult(
            is_technical_ai_role=True,
            is_relevant=True,
            relevance_reason="Valid technical engineering role with AI/ML software engineering requirements.",
            role_family=role,
            seniority=seniority,
            years_experience_min=3,
            education_requirement="Bachelor's degree in CS or related field",
            skills=skills,
        )

class OpenAICompatibleProvider(LLMProvider):
    """LangChain-powered OpenAI compatible LLM provider."""

    def __init__(self, base_url: str = None, api_key: str = None, model: str = None):
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

        if self.api_key:
            self.llm = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model,
                temperature=0.1,
                model_kwargs={"stream": False, "response_format": {"type": "json_object"}},
            )

            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert tech recruiter and AI job analyst.
Analyze both the Job Title AND full Job Description text to evaluate relevance and extract technical skills.

DEEP JOB RELEVANCE EVALUATION:
- Even if a job title sounds generic (e.g. "Software Engineer", "Data Engineer", "Backend Developer"), inspect the FULL description text: if it involves building, deploying, fine-tuning, or optimizing AI/ML/Data infrastructure, set "is_relevant": true and match to the appropriate Role Family.
- Set "is_technical_ai_role": false and "is_relevant": false for non-technical roles such as Video AI Editor, AI Content Creator, AI Copywriter, Marketing, etc.
- Provide a clear 1-sentence "relevance_reason".

Target Roles: AI Engineer, ML Engineer, MLOps Engineer, Data Scientist, Backend Engineer, Platform Engineer, Not Relevant / Non-Technical.
Seniority Levels: intern, junior, mid, senior, lead, unknown.
Skill Categories: language, framework, cloud, devops, database, ml_framework, other.
Requirement Types: required, preferred, mentioned.

Return JSON strictly in the following format:
{{
  "is_technical_ai_role": true,
  "is_relevant": true,
  "relevance_reason": "Role involves developing LLM application backends with PyTorch and FastAPI.",
  "role_family": "AI Engineer",
  "seniority": "mid",
  "years_experience_min": 3,
  "education_requirement": "Bachelor's degree in CS",
  "skills": [
    {{
      "name": "PyTorch",
      "category": "ml_framework",
      "requirement_type": "required",
      "evidence": "2+ years of experience with PyTorch for model training",
      "confidence": 0.95
    }}
  ]
}}"""),
                ("human", "Job Title: {title}\nJob Description:\n{description_text}"),
            ])

            self.chain = self.prompt | self.llm
        else:
            self.llm = None
            self.chain = None

    async def extract_job_info(self, title: str, description_text: str) -> AIJobExtractionResult:
        if not self.api_key or not self.llm:
            logger.warning("LLM_API_KEY not provided. Falling back to MockLLMProvider behavior.")
            return await MockLLMProvider().extract_job_info(title, description_text)

        raw_res = await self.chain.ainvoke({
            "title": title,
            "description_text": description_text[:4000],
        })

        content_text = str(raw_res.content).strip()
        cleaned_json_str = clean_json_codeblock(content_text)

        parsed_data = json.loads(cleaned_json_str)
        return AIJobExtractionResult.model_validate(parsed_data)
