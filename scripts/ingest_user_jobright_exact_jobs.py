import asyncio
import os
import sys
import logging
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import SessionLocal, Job, Company
from packages.schemas import NormalizedJobPost
from apps.crawler.normalizer import clean_html_to_text, normalize_canonical_url, compute_content_hash
from apps.crawler.store import save_normalized_job
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("user_jobright_exact_jobs")

EXACT_JOBRIGHT_POSTS = [
    # Australia - Remote Entry Level / Intern
    {
        "title": "Software Development Engineer",
        "company": "Jobright | GoDaddy",
        "domain": "godaddy.com",
        "location": "Australia (Remote)",
        "url": "https://careers.godaddy.net/job/software-development-engineer-australia-remote",
        "seniority": "Entry Level / Junior",
        "job_type": "Full-time",
        "salary": "AUD $110,000 - $130,000/yr",
        "description": """### Role Overview
GoDaddy is looking for a passionate Software Development Engineer (Entry Level) to join our distributed engineering team in Australia working 100% remotely. You will build high-scale domain registrar platforms, global DNS routing services, and AI-powered website building tools used by 20+ million customers worldwide.

### Responsibilities
- Design, build, and maintain backend microservices and RESTful APIs using Python, Go, and Java.
- Implement distributed caching, event streaming with Apache Kafka, and relational/NoSQL data models on AWS cloud infrastructure.
- Collaborate with global engineering, product, and AI teams to deliver resilient, highly available customer experiences.
- Participate in code reviews, automated unit/integration testing (pytest/JUnit), and continuous deployment pipelines (CI/CD with Docker & Kubernetes).

### Requirements
- Bachelor's or Master's degree in Computer Science, Software Engineering, or equivalent practical experience (0-2 years).
- Strong foundation in data structures, algorithms, object-oriented design, and concurrent programming.
- Hands-on experience with Python, Java, C++, TypeScript, or Go through internships, coursework, or open-source projects.
- Understanding of cloud services (AWS/GCP), containerization (Docker), and Git version control."""
    },
    {
        "title": "AI Trainer - Freelance Data Annotator",
        "company": "Jobright | Mindrift Data Annotation Projects",
        "domain": "mindrift.ai",
        "location": "Australia (Remote)",
        "url": "https://mindrift.ai/careers/ai-trainer-australia-remote",
        "seniority": "Entry Level",
        "job_type": "Part-time / Contract",
        "salary": "$45 - $65/hr",
        "description": """### About Mindrift
Mindrift builds cutting-edge AI data training pipelines for frontier AI models and LLM agent systems. We are seeking AI Trainers and Data Annotators based in Australia for flexible, remote projects.

### Responsibilities
- Evaluate, rank, and rewrite LLM-generated code, mathematical proofs, and technical responses for reasoning accuracy and safety alignment (RLHF / DPO).
- Construct high-quality domain-specific prompt-response pairs in Python, algorithms, and machine learning concepts.
- Identify model hallucinations, logic flaws, and edge-case failures in AI assistant workflows.

### Requirements
- Background in Computer Science, AI, Mathematics, or Computational Linguistics (Junior / New Grad welcome).
- Strong coding and debugging ability in Python, Java, or C++.
- Attention to detail and ability to work independently in a remote setting."""
    },

    # United States - Remote Entry Level / New Grad
    {
        "title": "Data Scientist - AI Evaluation",
        "company": "Jobright | GigFinder.ai",
        "domain": "gigfinder.ai",
        "location": "United States (Remote)",
        "url": "https://gigfinder.ai/members/job-detail?id=2662329&back=/jobs&jr_id=6a872fba25fc4e7ae3dabcd0",
        "seniority": "Entry Level / Junior",
        "job_type": "Contract",
        "salary": "$100/hr - $150/hr",
        "description": """### Overview
Mercor connects elite creative and technical talent with leading AI research labs. The Data Scientist - AI Evaluation role involves designing grading criteria, evaluating data science work, providing evidence-based feedback, and helping improve AI model performance.

- **Location**: United States (100% Remote)
- **Employment Type**: Contract ($100/hr - $150/hr)
- **Experience Level**: Entry Level / 1+ years exp
- **Jobright URL**: [View on Jobright](https://jobright.ai/jobs/info/6a872fba25fc4e7ae3dabcd0#overview)
- **Original Portal**: [Apply on GigFinder](https://gigfinder.ai/members/job-detail?id=2662329&back=/jobs&jr_id=6a872fba25fc4e7ae3dabcd0)

### Responsibilities
- Design precise, task-specific grading criteria for data science deliverables, including exploratory data analyses, statistical modeling work, machine learning pipelines, and A/B test write-ups.
- Evaluate AI-generated or human-created work against established criteria to ensure quality and consistency.
- Provide detailed written justifications for evaluations and scores to maintain transparency and accountability.
- Apply consistent, evidence-based judgment to ensure assessments are reproducible and defensible.
- Incorporate structured feedback from senior reviewers and iterate on submitted work for continuous improvement.
- Work independently and asynchronously to meet deadlines and improve AI model performance.

### Qualifications & Required Skills
- 1+ years of professional data science experience.
- Experience at a leading technology, research, or quantitative firm.
- Strong command of Python, SQL, Statistical Modeling, Machine Learning, Experimentation, and Data Science.
- Exceptional written communication skills and detail-oriented approach to evaluating complex AI workflows.
- Comfort receiving feedback and calibrating judgment against established evaluation standards.

### Benefits & Work Culture
- 100% Remote work.
- Work independently and asynchronously on cutting-edge AI LLM benchmarks.

### Company Profile: GigFinder.ai
AI job matching platform for jobs and contract work. Founded in 2025, Richmond, Virginia, US (Early Stage)."""
    },
    {
        "title": "Software Engineer – Entry Level",
        "company": "Jobright | VivSoft",
        "domain": "vivsoft.io",
        "location": "United States (Remote)",
        "url": "https://vivsoft.io/careers/software-engineer-entry-level-remote",
        "seniority": "New Grad / Entry Level",
        "job_type": "Full-time",
        "salary": "$85,000 - $105,000/yr",
        "description": """### About VivSoft
VivSoft delivers public-sector technology accelerators, cloud-native AI platforms, and open-source innovations. We are hiring Entry Level / New Grad Software Engineers to work remotely across the United States.

### Responsibilities
- Build modern web applications and cloud microservices using Python, FastAPI, React, TypeScript, and PostgreSQL.
- Develop containerized data processing pipelines on AWS/Azure using Docker and Kubernetes.
- Implement automated testing suites, secure API integrations, and CI/CD automation with GitHub Actions.
- Contribute to AI-assisted citizen intelligence and document processing workflows.

### Requirements
- BS or MS in Computer Science, Software Engineering, or related field (Graduating 2025/2026 or 0-1 year experience).
- Solid programming skills in Python, Java, JavaScript/TypeScript, or Go.
- Understanding of database design (SQL/PostgreSQL), RESTful APIs, and Git.
- Must be eligible to work remotely in the United States."""
    },

    # Canada Remote Intern (Cohere)
    {
        "external_id": "6a57eb4c3330ca6f993c1fb5",
        "title": "Machine Learning Intern/Co-op (Winter 2027)",
        "company": "Jobright | Cohere",
        "domain": "cohere.com",
        "location": "Canada (Remote)",
        "url": "https://jobs.ashbyhq.com/cohere/36d1f52f-8270-4652-adf5-5303a0ff341b/application?utm_source=jobright&jr_id=6a57eb4c3330ca6f993c1fb5",
        "seniority": "Intern",
        "job_type": "Internship / Full-time Co-op",
        "salary": "CAD $45 - $60/hr ($75/wk lunch stipend + $500 home office)",
        "description": """### Overview
Cohere is the leading security-first enterprise AI unicorn ($7B valuation). As a Machine Learning Intern/Co-op (Winter 2027), you will design and implement novel research ideas, build distributed training and deployment pipelines, and contribute to shipping state-of-the-art foundation models to production.

- **Location**: Canada (100% Remote)
- **Employment Type**: Internship / Co-op (Winter 2027)
- **Experience Level**: Intern / Student
- **Jobright URL**: [View on Jobright](https://jobright.ai/jobs/info/6a57eb4c3330ca6f993c1fb5#overview)
- **Official ATS Portal**: [Apply on AshbyHQ](https://jobs.ashbyhq.com/cohere/36d1f52f-8270-4652-adf5-5303a0ff341b/application?utm_source=jobright&jr_id=6a57eb4c3330ca6f993c1fb5)

### Responsibilities
- Design, train, and improve upon cutting-edge autoregressive foundation models.
- Develop novel techniques to train and serve models safer, better, and faster.
- Train extremely large-scale models on massive multi-modal and NLP datasets.
- Explore continual and active learning strategies for streaming data.
- Learn from experienced senior machine learning technical staff and collaborate with product engineering.

### Qualifications & Technical Skills
- Proficiency in Python and modern ML frameworks: TensorFlow, TF-Serving, JAX, and XLA/MLIR.
- Experience using large-scale distributed training strategies on GPU/TPU clusters.
- Strong familiarity with autoregressive sequence models and Transformers architecture.
- Demonstrated passion for applied NLP models and generative AI systems.
- Must be a student enrolled in a post-secondary program available for a full-time 3-6 month internship/co-op.

### Preferred Experience
- Writing custom GPU kernels using CUDA.
- Experience training foundation models on Google Cloud TPUs.
- Research publications at top-tier AI venues (NeurIPS, ICML, ICLR, ACL, EMNLP, MLSys).

### Benefits & Stipends
- Weekly lunch stipend of $75 CAD / week.
- Full health & dental coverage, RRSP matching, and $500 home office setup allowance.
- 6 weeks paid vacation (30 working days) + annual education & conference travel stipend."""
    },
    {
        "title": "Graduate Backend Software Engineer",
        "company": "Jobright | Monzo Bank",
        "domain": "monzo.com",
        "location": "United Kingdom (Remote)",
        "url": "https://monzo.com/careers/graduate-backend-engineer-uk-remote",
        "seniority": "New Grad / Junior",
        "job_type": "Full-time",
        "salary": "£50,000 - £65,000/yr",
        "description": """### About Monzo
Monzo is one of the UK's fastest growing digital banks. We are looking for Graduate Backend Engineers to work remotely across the UK.

### Responsibilities
- Write high-concurrency microservices in Go and Python deployed on Kubernetes and AWS.
- Design resilient event-driven architectures with Apache Kafka and Cassandra.
- Build secure, scalable banking APIs supporting millions of active transactions daily.

### Requirements
- Degree in Computer Science, Mathematics, or Engineering (New Grad 2025/2026).
- Strong understanding of algorithms, systems programming, and distributed computing."""
    }
]

async def main():
    logger.info("Ingesting exact multi-country Jobright remote positions...")
    db = SessionLocal()
    provider = MockLLMProvider()

    for item in EXACT_JOBRIGHT_POSTS:
        full_desc = item["description"]
        clean_text = clean_html_to_text(full_desc)
        content_hash = compute_content_hash(clean_text)

        norm_post = NormalizedJobPost(
            external_id=item.get("external_id") or f"jobright-exact-{item['domain']}-{item['title'].lower().replace(' ', '-')}",
            canonical_url=normalize_canonical_url(item["url"]),
            company_name=item["company"],
            title=item["title"],
            location=item["location"],
            description_raw=full_desc,
            description_text=clean_text,
            content_hash=content_hash,
        )

        job, is_new = save_normalized_job(db, norm_post)
        analysis = await extract_and_save_job(db, job, provider)
        logger.info(f"Ingested: '{job.title}' ({job.company.name}) | Loc: '{job.location}' | Sen: '{analysis.seniority}' | Rel: {analysis.is_relevant}")

    db.close()
    logger.info("🎉 Ingestion of exact multi-country Jobright remote positions complete!")

if __name__ == "__main__":
    asyncio.run(main())
