# AI Job Intelligence Platform

An end-to-end autonomous AI Job Intelligence and Career Analytics platform that continuously crawls, normalizes, deduplicates, analyzes, and categorizes AI/ML, Data, and Software Engineering roles across the global job market.

---

## 📚 Documentation Index

For complete architectural specifications, site-by-site crawler guides, reverse-engineering details, and blueprints, consult the documentation suite in [`docs/`](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/):

- 📘 **[Master Handover & Architecture Guide](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/PROJECT_HANDOVER.md)**: System overview, end-to-end data pipeline, component responsibilities, and monorepo structure.
- 🕷️ **[Crawler Knowledge Base & Site-by-Site Guide](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/CRAWLER_KNOWLEDGE_BASE.md)**: Reverse-engineered APIs, session cookie quirks (`401 Cookie not found`), deep-linking specifications, paywall vault detection, and multi-country filters for **Jobright**, **Foorilla**, **AshbyHQ**, **Greenhouse**, **Lever**, and **TopCV**.
- 💡 **[Domain Intelligence & Capstone Blueprints](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/DOMAIN_INTELLIGENCE_GUIDE.md)**: Market intelligence across 6 AI verticals, junior/intern expectation matrices, and 6 production-grade capstone project blueprints with quantifiable SLAs.
- ⚡ **[Operations Cheatsheet & Maintenance Manual](file:///Users/vutl2004/Documents/LLMOps/JobCrawler/docs/OPERATIONS_CHEATSHEET.md)**: Command reference for starting services, executing crawlers, querying API endpoints, and running test suites.

---

## 🚀 Quick Start (Local Execution)

### 1. Start the FastAPI Backend (Port 8000)
```bash
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python -m uvicorn apps.api.main:app --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

### 2. Start the Next.js Web Dashboard (Port 3000)
```bash
npm run dev --prefix apps/web -- -p 3000
```
- Web Application: `http://localhost:3000`

---

## 🏗️ Monorepo Structure

```
.
├── apps/
│   ├── api/                 # FastAPI REST API (Job querying, domain blueprints, skill analytics)
│   ├── crawler/             # Ingestion monitors (AshbyHQ, Greenhouse, Lever, Jobright, Foorilla, TopCV)
│   ├── analyzer/            # Fast regex pre-filter + LLM extraction & schema validation
│   └── web/                 # Next.js 16 (App Router, TailwindCSS, Glassmorphism UI)
├── docs/                    # Complete architectural & operational documentation suite
│   ├── PROJECT_HANDOVER.md
│   ├── CRAWLER_KNOWLEDGE_BASE.md
│   ├── DOMAIN_INTELLIGENCE_GUIDE.md
│   └── OPERATIONS_CHEATSHEET.md
├── packages/
│   ├── database/            # SQLAlchemy 2.0 ORM models & session management
│   └── schemas/             # Shared Pydantic schemas (NormalizedJobPost, ExtractedJobAnalysis)
├── scripts/                 # Ingestion, crawling, and database maintenance scripts
├── tests/                   # Pytest test suite & fixtures
├── test_jobcrawler.db       # Active SQLite database with 2,450+ verified technical jobs
└── Makefile                 # Build and development commands
```

---

## 🧪 Testing & Validation

```bash
# Run backend pytest suite
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/pytest tests/ -v

# Run frontend production build
npm run build --prefix apps/web
```
