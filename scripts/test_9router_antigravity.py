import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apps.analyzer.provider import OpenAICompatibleProvider

async def main():
    base_url = "http://127.0.0.1:20128/v1"
    api_key = "your_llm_api_key_here"
    model = "ag/gemini-3.6-flash-high"

    print(f"Connecting to 9router at {base_url} using model '{model}'...")
    provider = OpenAICompatibleProvider(
        base_url=base_url,
        api_key=api_key,
        model=model,
    )

    sample_title = "Senior AI Engineer (LLM & Agent Systems)"
    sample_desc = """
    We are seeking a Lead / Senior AI Engineer to design and deploy agentic AI platforms.
    
    Responsibilities:
    - Build production LLM systems with PyTorch, LangChain, and FastAPI.
    - Deploy scalable microservices to AWS EKS using Docker, Kubernetes, and Terraform.
    - Implement vector search with PostgreSQL/pgvector and Redis.
    
    Requirements:
    - 4+ years of experience in AI/ML Engineering.
    - Deep expertise in Python, PyTorch, CUDA, and Docker.
    - Strong background in Kubernetes and CI/CD pipelines.
    - Master's or Bachelor's degree in Computer Science or related field.
    """

    result = await provider.extract_job_info(sample_title, sample_desc)

    print("\n--- 9Router Antigravity Extraction Result ---")
    print(f"Role Family : {result.role_family.value}")
    print(f"Seniority   : {result.seniority.value}")
    print(f"Min Exp     : {result.years_experience_min} years")
    print(f"Education   : {result.education_requirement}")
    print(f"Total Skills: {len(result.skills)}")
    print("\nExtracted Skills:")
    for skill in result.skills:
        print(f" - [{skill.category.value.upper()}] {skill.name} ({skill.requirement_type.value}): \"{skill.evidence}\"")

if __name__ == "__main__":
    asyncio.run(main())
