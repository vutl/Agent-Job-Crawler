# AI Job Intelligence Platform

An end-to-end AI Job Intelligence platform that continuously collects public job postings, normalizes job descriptions, extracts explicit skill requirements using structured LLMs, aggregates market demand by engineering role, and displays insights via an interactive dashboard.

## Target Architecture

```
Public Career Pages / ATS APIs (Greenhouse, Lever)
               │
               ▼
        Crawl Scheduler
               │
               ▼
          Redis Queue
         /           \
        ▼             ▼
  HTTP Crawler   Browser Crawler (Playwright)
        \             /
         ▼           ▼
        Job Normalizer & Content Hasher
               │
               ▼
          PostgreSQL Database
               │ (New / Changed Jobs)
               ▼
         Analysis Queue
               │
               ▼
       AI Analysis Worker (LLM Provider Adapter)
               │
               ▼
     Structured Skill & Seniority Data
               │
       ┌───────┴───────┐
       ▼               ▼
 FastAPI Service   Aggregation Jobs
       │
       ▼
Next.js Web Dashboard
```

## Supported Roles (V1 Scope)
- **AI Engineer**
- **ML Engineer**
- **MLOps Engineer**
- **Data Scientist**

## Monorepo Layout
```
.
├── apps/
│   ├── api/                 # FastAPI REST API
│   ├── crawler/             # Ingestion workers & ATS monitors
│   ├── analyzer/            # LLM extraction & schema validation
│   └── web/                 # Next.js Web Dashboard
├── packages/
│   └── schemas/             # Shared Pydantic & JSON Schemas
├── infra/
│   ├── docker/              # Dockerfiles & Compose setups
│   └── k8s/                 # Kubernetes manifests (kind/minikube/EKS)
├── tests/
│   ├── fixtures/            # Saved HTML & JSON fixtures for deterministic tests
│   └── integration/         # Integration test suite
├── docker-compose.yml       # Local PostgreSQL + Redis development environment
└── Makefile                 # Convenient commands for setup, linting, and testing
```

## Getting Started (Local Development)

### 1. Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (for Web Dashboard)

### 2. Start Local Infrastructure
```bash
docker compose up -d postgres redis
```

### 3. Run Ingestion & Analysis Workers
See README inside `apps/crawler` and `apps/analyzer`.

---
*Built following the AI Job Intelligence Project Blueprint.*
