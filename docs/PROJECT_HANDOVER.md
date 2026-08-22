# AI Job Intelligence Platform — Master Handover & Architecture Guide

> **Target Audience**: Antigravity AI Coding Assistants, Lead Engineers, and AI System Developers continuing work on this repository.
> **Last Updated**: August 2026

---

## 1. Executive Summary & Vision

The **AI Job Intelligence Platform** is an enterprise-grade agentic system designed to continuously crawl, normalize, deduplicate, filter, and analyze artificial intelligence, machine learning, data engineering, and software engineering opportunities from across the global job market.

### Core Objectives
1. **Multi-Source Autonomous Aggregation**: Ingest from major aggregators (**Jobright**, **Foorilla**, **TopCV**) and direct corporate ATS boards (**AshbyHQ**, **Greenhouse**, **Lever**, **Workday**).
2. **Strict Quality & Technical Relevance Filtering**: Two-tier filtering pipeline (Fast Regex/Heuristic Pre-filter + Deep LLM Analysis) to eliminate non-technical corporate noise (sales, marketing, HR) and accurately classify technical sub-disciplines.
3. **Paywall Vault & Public Job Segregation**: Transparently detect login-walls/paywalls and isolate gated posts into a dedicated Paywall Vault while displaying clean, publicly accessible positions on the main explorer.
4. **Domain & Capstone Project Blueprints**: Provide quantitative intelligence on what skills industry verticals (Agentic AI, Computer Vision, Healthcare, Fintech, MLOps, Search/RecSys) demand at the Intern/Junior level, paired with production-grade Capstone Project blueprints to help candidates get hired.
5. **Authentic Deep-Linking**: Provide verified links pointing to authentic corporate ATS apply portals alongside aggregator overview deep-links.

---

## 2. System Architecture & Tech Stack

```mermaid
flowchart TD
    subgraph Ingestion Layer
        A1[Jobright Monitor<br/>swan-api.jobright.ai]
        A2[Foorilla Monitor<br/>HTML & Paywall Parsing]
        A3[AshbyHQ Monitor<br/>Cohere, Perplexity, ElevenLabs...]
        A4[Greenhouse Monitor<br/>Scale AI, Stripe, Figma, Cloudflare...]
        A5[Lever Monitor<br/>Spotify, Anthropic...]
        A6[TopCV Monitor<br/>Vietnam Tech Market]
    end

    subgraph Processing & Analysis Pipeline
        B1[Normalizer & SHA256 Content Hasher] --> B2[Fast Regex Pre-filter]
        B2 -- Rejected --> B3[Non-Relevant Archive]
        B2 -- Passed --> B4[LLM / MockLLM Provider]
        B4 --> B5[Role & Seniority Classifier]
        B4 --> B6[Skill & Evidence Span Extractor]
    end

    subgraph Data Store
        C1[(SQLite Database<br/>test_jobcrawler.db)]
        C2[Jobs Table]
        C3[Companies Table]
        C4[Skills Table]
        C5[JobAnalysis Table]
        C6[JobSkills Table]
    end

    subgraph API & Serving Layer
        D1[FastAPI Backend :8000]
        D2[/api/v1/jobs - Query & Pagination]
        D3[/api/v1/intelligence/domains - Blueprints]
        D4[/roles/{role}/skills - Skill Analytics]
        D5[/system/data-freshness - Metrics]
    end

    subgraph Presentation Layer
        E1[Next.js 16 App Router :3000]
        E2[AI Job Market Explorer]
        E3[Domain & Project Blueprints Hub]
        E4[Tech Stack Analytics Dashboard]
        E5[Paywall Vault]
        E6[Rich Markdown JD Drawer]
    end

    Ingestion Layer --> Processing & Analysis Pipeline
    Processing & Analysis Pipeline --> Data Store
    Data Store --> API & Serving Layer
    API & Serving Layer --> Presentation Layer
```

### Component Breakdown

| Layer | Technology | Primary Location | Key Responsibilities |
|---|---|---|---|
| **Database** | SQLite + SQLAlchemy 2.0 | `packages/database/` | Relational storage for jobs, companies, skills, evidence spans, and analysis results. |
| **Crawler Engine** | Python 3.11, `httpx`, `asyncio`, `BeautifulSoup4` | `apps/crawler/` | Multi-source asynchronous monitors, HTML parsing, canonical URL normalization, and SHA256 hashing. |
| **Analyzer Pipeline**| Regex Pre-filter, LLM Extraction | `apps/analyzer/` | High-speed regex filtering followed by LLM skill and evidence span extraction. |
| **API Backend** | FastAPI, Uvicorn, Pydantic v2 | `apps/api/` | RESTful endpoints with limit up to 5,000 items, domain intelligence, and skill statistics. |
| **Web Frontend** | Next.js 16 (Turbopack), React 19, TailwindCSS | `apps/web/` | Glassmorphism dashboard, multi-field instant search, tab navigation, and markdown job description drawers. |

---

## 3. Quick Start & Execution Reference

### Starting Services

```bash
# 1. Start FastAPI Backend (Port 8000)
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python -m uvicorn apps.api.main:app --port 8000 --reload

# 2. Start Next.js Frontend (Port 3000)
npm run dev --prefix apps/web -- -p 3000
```

### Running Crawlers & Ingestion Scripts

```bash
# Ingest all Global Direct ATS (AshbyHQ + Greenhouse)
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/ingest_global_remote_network.py

# Ingest Deep Remote Network from Jobright
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/crawl_remote_deep_network.py

# Ingest Exact Verified Multi-Country Jobs (Cohere, Agility PR, GigFinder, GoDaddy, VivSoft)
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/ingest_user_jobright_exact_jobs.py

# Ingest All Foorilla Snapshots & Leiden/Nokia Bell Labs/KIS Positions
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/ingest_all_real_data.py

# Re-analyze and re-classify all jobs in database
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/reanalyze_database.py
```

### Running Automated Tests

```bash
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/pytest tests/ -v
```

---

## 4. Key Documentation Index

For detailed guidelines and deep-dive technical references, consult the following dedicated documents in `docs/`:

1. **[`docs/CRAWLER_KNOWLEDGE_BASE.md`](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/CRAWLER_KNOWLEDGE_BASE.md)**:
   - Comprehensive site-by-site breakdown for **Jobright**, **Foorilla**, **AshbyHQ**, **Greenhouse**, **Lever**, and **TopCV**.
   - Reverse-engineered API routes, session authentication quirks, cookie error 41001, deep-linking rules, and paywall detection.
2. **[`docs/DOMAIN_INTELLIGENCE_GUIDE.md`](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/DOMAIN_INTELLIGENCE_GUIDE.md)**:
   - Detailed specifications of the 6 AI industry verticals, junior expectations, and capstone blueprints with SLAs.
3. **[`docs/OPERATIONS_CHEATSHEET.md`](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/OPERATIONS_CHEATSHEET.md)**:
   - Operations cheatsheet, schema reference, troubleshooting, and maintenance commands.
