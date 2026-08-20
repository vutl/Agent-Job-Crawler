import os
import json
import logging
import re
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
    """Mock LLM Provider for deterministic testing and offline extraction."""

    async def extract_job_info(self, title: str, description_text: str) -> AIJobExtractionResult:
        title_lower = title.lower()

        # 1. Non-technical role filters
        non_tech_patterns = [
            r"\bstatutory\b", r"\btax\b", r"\bpayroll\b", r"\baccounting\b|\baccountant\b",
            r"\baudit\b", r"\bfinance\b|\bfinancial\s+systems\b", r"\bscm\b|\bsupply\s+chain\b",
            r"\bpayment\s+operations\b", r"\boperations\s+(?:lead|manager|director)\b",
            r"\bstrategic\s+partner\b|\bpartner\s+manager\b", r"\baccount\s+executive\b",
            r"\bsales\b", r"\brecruiter\b|\bhr\b|\btalent\b", r"\blegal\b|\bcounsel\b",
            r"\bcustomer\s+(?:success|support|service|engineer)\b",
            r"\bvideo\s+editor\b|\bcontent\s+creator\b|\bcopywriter\b|\bmarketing\b",
            r"\bproduct\s+manager\b(?!.*(?:ai|ml|machine\s+learning))",
        ]

        for pattern in non_tech_patterns:
            if re.search(pattern, title_lower):
                return AIJobExtractionResult(
                    is_technical_ai_role=False,
                    is_relevant=False,
                    relevance_reason=f"Role '{title}' matches corporate/non-technical pattern.",
                    role_family=RoleFamily.NOT_RELEVANT,
                    seniority=SeniorityLevel.UNKNOWN,
                    years_experience_min=0,
                    education_requirement=None,
                    skills=[],
                )

        # 2. Determine Role Family
        if "mlops" in title_lower or "ai platform" in title_lower or "ml infra" in title_lower:
            role = RoleFamily.MLOPS_ENGINEER
        elif "machine learning" in title_lower or re.search(r"\bml\s+engineer\b", title_lower) or "deep learning" in title_lower:
            role = RoleFamily.ML_ENGINEER
        elif "data scientist" in title_lower or "research scientist" in title_lower or "ai researcher" in title_lower:
            role = RoleFamily.DATA_SCIENTIST
        elif "ai" in title_lower or "artificial intelligence" in title_lower or "llm" in title_lower:
            role = RoleFamily.AI_ENGINEER
        elif "data engineer" in title_lower:
            role = RoleFamily.DATA_SCIENTIST
        elif "software engineer" in title_lower or "backend" in title_lower or "infrastructure" in title_lower or "systems" in title_lower:
            # Check if description relates to data/AI
            if any(w in description_text.lower() for w in ["ai", "ml", "machine learning", "data", "model", "pipeline", "pytorch"]):
                role = RoleFamily.AI_ENGINEER
            else:
                role = RoleFamily.AI_ENGINEER
        else:
            role = RoleFamily.AI_ENGINEER

        # 3. Determine Seniority
        desc_lower = description_text.lower()
        if "intern" in title_lower or "co-op" in title_lower or "trainee" in title_lower or "internship" in title_lower:
            seniority = SeniorityLevel.INTERN
        elif (
            "junior" in title_lower or "entry" in title_lower or "new grad" in title_lower or "[en]" in title_lower or
            "graduate" in title_lower or "associate" in title_lower or "level 1" in title_lower or "developer i" in title_lower or
            "engineer i" in title_lower or "entry level" in desc_lower or "new grad" in desc_lower or "0-1 year" in desc_lower or
            "0-2 years" in desc_lower or "1+ years" in desc_lower or "1+ years exp" in desc_lower
        ):
            seniority = SeniorityLevel.JUNIOR
        elif "staff" in title_lower or "principal" in title_lower or "lead" in title_lower or "director" in title_lower or "head" in title_lower:
            seniority = SeniorityLevel.LEAD
        elif "senior" in title_lower or "sr" in title_lower or "[se]" in title_lower or "sr." in title_lower:
            seniority = SeniorityLevel.SENIOR
        else:
            seniority = SeniorityLevel.MID

        # 4. Extract Skills using word boundaries
        skills = []
        desc_lower = description_text.lower()

        keywords = [
            (r"\bpython\b", "Python", SkillCategory.LANGUAGE),
            (r"\bpytorch\b", "PyTorch", SkillCategory.ML_FRAMEWORK),
            (r"\btensorflow\b", "TensorFlow", SkillCategory.ML_FRAMEWORK),
            (r"\bkubernetes\b|\bk8s\b", "Kubernetes", SkillCategory.DEVOPS),
            (r"\bdocker\b", "Docker", SkillCategory.DEVOPS),
            (r"\baws\b", "AWS", SkillCategory.CLOUD),
            (r"\bgcp\b|\bgoogle\s+cloud\b", "GCP", SkillCategory.CLOUD),
            (r"\bazure\b", "Azure", SkillCategory.CLOUD),
            (r"\bfastapi\b", "FastAPI", SkillCategory.FRAMEWORK),
            (r"\bpostgresql\b|\bpostgres\b", "PostgreSQL", SkillCategory.DATABASE),
            (r"\blangchain\b", "LangChain", SkillCategory.ML_FRAMEWORK),
            (r"\bllamaindex\b", "LlamaIndex", SkillCategory.ML_FRAMEWORK),
            (r"\btransformers\b|\bhuggingface\b", "Hugging Face", SkillCategory.ML_FRAMEWORK),
            (r"\bspark\b|\bpyspark\b", "Apache Spark", SkillCategory.FRAMEWORK),
            (r"\bkafka\b", "Apache Kafka", SkillCategory.FRAMEWORK),
            (r"\bairflow\b", "Apache Airflow", SkillCategory.DEVOPS),
            (r"\bsql\b", "SQL", SkillCategory.LANGUAGE),
            (r"\bc\+\+\b", "C++", SkillCategory.LANGUAGE),
            (r"\bgolang\b|\bgo\b", "Go", SkillCategory.LANGUAGE),
            (r"\brust\b", "Rust", SkillCategory.LANGUAGE),
        ]

        for regex, canonical, cat in keywords:
            if re.search(regex, desc_lower) or re.search(regex, title_lower):
                # Search for surrounding sentence as evidence
                evidence = f"Required experience with {canonical}"
                match = re.search(rf"([^.\n]*?{regex}[^.\n]*)", desc_lower)
                if match:
                    evidence = match.group(0).strip().capitalize()
                    if len(evidence) > 120:
                        evidence = evidence[:117] + "..."

                skills.append(
                    ExtractedSkill(
                        name=canonical,
                        category=cat,
                        requirement_type=RequirementType.REQUIRED,
                        evidence=evidence,
                        confidence=0.95,
                    )
                )

        return AIJobExtractionResult(
            is_technical_ai_role=True,
            is_relevant=True,
            relevance_reason="Valid technical engineering role with AI/ML software engineering requirements.",
            role_family=role,
            seniority=seniority,
            years_experience_min=3 if seniority in [SeniorityLevel.SENIOR, SeniorityLevel.LEAD] else 1,
            education_requirement="Bachelor's or Master's degree in CS, AI, or related field",
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
