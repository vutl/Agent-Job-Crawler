# Operations Cheatsheet & Maintenance Manual

> **Purpose**: Quick command and reference guide for system startup, data ingestion, database maintenance, API endpoints, and troubleshooting.

---

## 1. Quick Command Cheatsheet

### 1.1 Starting Services

```bash
# Start FastAPI Backend (Port 8000)
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python -m uvicorn apps.api.main:app --port 8000 --reload

# Start Next.js Frontend (Port 3000)
npm run dev --prefix apps/web -- -p 3000
```

### 1.2 Ingestion & Crawling Commands

```bash
# 1. Global Direct ATS (AshbyHQ + Greenhouse)
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/ingest_global_remote_network.py

# 2. Deep Remote Network from Jobright
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/crawl_remote_deep_network.py

# 3. Exact Multi-Country Jobright Roles (Cohere, Agility PR, GigFinder, GoDaddy, VivSoft, Monzo)
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/ingest_user_jobright_exact_jobs.py

# 4. Foorilla HTML Snapshots & European Academic / Research Portals
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/ingest_all_real_data.py

# 5. Full Database Re-Analysis & Classification
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/python scripts/reanalyze_database.py
```

### 1.3 Testing & Quality Verification

```bash
# Run full Pytest suite
DATABASE_URL="sqlite:///./test_jobcrawler.db" .venv/bin/pytest tests/ -v

# Run Next.js TypeScript & Production Build
npm run build --prefix apps/web
```

---

## 2. API Endpoints Reference (`http://localhost:8000`)

| Method | Endpoint | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/api/v1/jobs` | `skip=0`, `limit=500` (max 5000), `locked_only=false` | Fetches normalized and analyzed job items. Use `locked_only=true` for Paywall Vault. |
| `GET` | `/api/v1/intelligence/domains` | None | Returns the 6 AI domain blueprints, junior expectation matrices, and capstone templates. |
| `GET` | `/roles/{role_family}/skills` | `role_family` (e.g. `ai_ml`, `data_engineer`, `software_engineer`) | Returns top required skills and frequencies for a role family. |
| `GET` | `/system/data-freshness` | None | Returns real-time ingestion counters (`total_jobs`, `active_jobs`, `analyzed_jobs`, `latest_job_crawled_at`). |
| `GET` | `/health` | None | Service health status. |

---

## 3. Database Schema Reference (`packages/database/models.py`)

- **`Job`**: Primary record containing `id`, `external_id`, `canonical_url`, `company_id`, `title`, `location`, `description_raw`, `description_text`, `content_hash`, `crawled_at`, `is_active`.
- **`Company`**: Company record containing `id`, `name`, `domain`, `created_at`.
- **`JobAnalysis`**: Analysis results containing `id`, `job_id`, `role_family`, `seniority`, `salary_currency`, `salary_min`, `salary_max`, `is_relevant`, `is_gated`, `paywall_type`, `analyzed_at`.
- **`Skill`**: Canonical skill definitions (`id`, `name`, `category`).
- **`JobSkill`**: Many-to-many relationship linking `job_id` to `skill_id` with `is_required` and `evidence_span`.

---

## 4. Git & Commit Guidelines

- **Remote Origin**: `https://github.com/vutl/Agent-Job-Crawler.git`
- **Main Branch**: `main`
- Always verify that the Next.js build passes (`npm run build --prefix apps/web`) and the pytest suite passes before committing.
