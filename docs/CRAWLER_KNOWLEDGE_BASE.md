# Crawler Knowledge Base & Site-by-Site Operational Guide

> **Purpose**: This document captures all reverse-engineered architectures, site-specific behaviors, quirks, authentication requirements, and critical design rules discovered across all crawled job sources.

---

## 1. Jobright (`jobright.ai`)

### 1.1 Architecture & Reverse-Engineered Network Layer
- **Frontend Stack**: Next.js (SSR + React Chunks).
- **Backend API**: `https://swan-api.jobright.ai`
- **Key Public Endpoints**:
  - `GET https://swan-api.jobright.ai/swan/recommend/landing/jobs`: Returns 20 generic landing jobs. Unauthenticated calls return default US onsite/hybrid positions.
  - `POST https://swan-api.jobright.ai/swan/recommend/similar/jobs`: Body `{"jobId": "<24-hex-id>"}`. **Publicly accessible (HTTP 200)** without authentication. This is the **primary discovery engine** for traversing Jobright's recommendation graph.
- **Protected / Session-Gated Endpoints**:
  - `POST https://swan-api.jobright.ai/swan/landing/basic/pref`: Sets user search filters (workModel, country, seniority). Returns `{"success":false, "errorCode":41001, "errorMsg":"Cookie not found"}` if called without an active session cookie.
  - `GET https://jobright.ai/jobs/info/{jobId}`: Requires active Jobright session cookies in the browser.

### 1.2 Authentication & User Session Quirk (The "Sad Face / 401 Cookie Not Found" Behavior)
- **Symptom**: Opening `https://jobright.ai/jobs/info/{jobId}` in a fresh/unauthenticated browser tab displays a sad-face icon (*"It seems that this job is no longer available. Explore recommended ones to find some you'd like!"*) and opens a Google Sign-in popup in the top right (`Sign in to jobright.ai with google.com`).
- **Root Cause**: Jobright protects its detail pages with a soft session wall. When unauthenticated, the Next.js page receives `401 Cookie not found` from `swan-api.jobright.ai`.
- **Resolution**:
  1. Once the user signs in to Jobright with their Google account once in that browser window, all `https://jobright.ai/jobs/info/{jobId}#overview` links load immediately with full match percentage, skills, and company insights.
  2. All generated Jobright deep-links **MUST** use verified 24-character hexadecimal IDs (e.g. `6a872fba25fc4e7ae3dabcd0`, `6a57eb4c3330ca6f993c1fb5`, `6a86048a74e02153f1459e14`).
  3. Never generate placeholder slug URLs (e.g. `jobright-exact-...`) as Jobright's router will throw a 404.

### 1.3 Deep-Linking Specification for Jobright
Jobright jobs in the UI should always offer:
1. **Overview & AI Match**: `https://jobright.ai/jobs/info/{24_hex_id}#overview`
2. **Company Profile & Funding**: `https://jobright.ai/jobs/info/{24_hex_id}#company`
3. **Official Apply Portal (Direct ATS Link)**: The authentic ATS redirect URL (AshbyHQ, Rippling, Greenhouse, Lever, Workday) if available.

### 1.4 Data Extraction from Jobright Payload
- **Company Name**: Found in `item['companyResult']['companyName']` or `item['jobResult']['companyAlias']`.
- **Company Funding & Details**: Found in `item['companyResult']` (`fundraisingTotalFunding`, `companySize`, `companyFoundYear`, `leadership`, `grating`).
- **Remote Work Model**: Check `jr.get('isRemote') is True` OR `"Remote" in str(jr.get('workModel'))` OR `"Remote" in str(jr.get('jobLocation'))`.
- **Location Normalization**: When `isRemote` is True, format as `{Country} (Remote)` (e.g. `Canada (Remote)`, `United States (Remote)`, `Australia (Remote)`).

### 1.5 Multi-Country Search Quirks on Jobright Web UI
- On Jobright's website search interface, the user can **only select one country at a time** (e.g., United States OR Canada OR Australia OR United Kingdom).
- To capture all positions across target geographies without missing remote roles, the crawler uses **multi-hop recursive discovery** starting from verified country seed jobs.

---

## 2. Foorilla (`foorilla.com`)

### 2.1 Paywall / Login-Wall Detection
- Foorilla employs a two-tier job structure:
  1. **Direct Employer Forwarding Jobs**: Publicly accessible jobs where `<a class="btn btn-primary btn-sm" href="/hiring/jobs/{id}/apply/">` redirects directly to the authentic employer portal (e.g., Nokia Bell Labs, Leiden University, Skyworks, Vaillant Group).
  2. **Gated / Paywalled Jobs**: Posts requiring a paid subscription or Google login to view contact details or apply.
- **Handling Strategy**:
  - The system automatically detects paywalled content via heuristic markers (`PAYWALL_DETECTED`, `Sign in to continue`, `Authentication required`).
  - Gated jobs are segregated into the **Paywall Vault** (`locked_only=true`), preserving the clean public explorer for 100% verified accessible positions.

### 2.2 HTML Snapshot Ingestion
- Foorilla postings provided via raw HTML snapshots (`format.txt`, `format2.txt`, `format3.txt`, `format4.txt`) are parsed using `FoorillaMonitor.parse_foorilla_html_snapshot()`.
- Extracts: Title, Company Name, Location, Description, Extracted Skills, and Canonical Apply URLs.

---

## 3. Direct ATS Integrations (Frontier AI & Enterprise Tech)

Direct ATS integrations bypass aggregator gatekeeping and provide 100% authentic, real-time job availability with zero login requirements.

### 3.1 AshbyHQ Monitor (`apps/crawler/monitors/ashby.py`)
- **API Pattern**: `GET https://api.ashbyhq.com/posting-api/job-board/{board_token}`
- **Active Board Tokens**:
  - `cohere` (Cohere — Enterprise AI Unicorn, 140+ live roles, Remote Canada/US/UK)
  - `perplexity` (Perplexity AI — AI Search Engine, 100+ live roles)
  - `elevenlabs` (ElevenLabs — Voice & Audio AI, 250+ live roles)
  - `linear` (Linear — Modern Project Management, 30+ live roles)
  - `baseten` (Baseten — High-Performance ML Inference, 75+ live roles)
  - `modal` (Modal — Serverless GPU Cloud, 30+ live roles)
  - `suno` (Suno — Generative Music AI, 60+ live roles)
- **Data Normalization**:
  - `apply_url`: `https://jobs.ashbyhq.com/{board_token}/{job_id}`
  - `is_remote`: Checked via `j.get('isRemote')` and `j.get('location')`.

### 3.2 Greenhouse Monitor (`apps/crawler/monitors/greenhouse.py`)
- **API Pattern**: `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`
- **Active Board Tokens**:
  - `cloudflare` (Cloudflare — Global Cloud & Edge AI, 300+ live roles)
  - `scaleai` (Scale AI — Data Engine for AI, 200+ live roles)
  - `figma` (Figma — Design Platforms, 160+ live roles)
  - `stripe` (Stripe — Financial Infrastructure, 500+ live roles)
  - `datarobot` (DataRobot — Enterprise AI Platform, 20+ live roles)

### 3.3 Lever Monitor (`apps/crawler/monitors/lever.py`)
- **API Pattern**: `GET https://api.lever.co/v0/postings/{board_token}`
- **Active Board Tokens**: `spotify`, `anthropic`, `temporal`, `replit`.

---

## 4. TopCV (`topcv.vn`)

### 4.1 Vietnam Tech Market Crawling
- **API / Search Pattern**: Scrapes listings from `https://www.topcv.vn/tim-kiem-viec-lam` with query parameters `tu-khoa` (AI Engineer, Machine Learning, Data Engineer) and `kinh-nghiem`.
- **Deduplication**: Uses SHA256 content hashing on cleaned job descriptions to eliminate cross-posted duplicates.

---

## 5. Filtering & Classification Rules

### 5.1 Seniority Classification Heuristics
Located in `apps/analyzer/provider.py`:
- **Intern**: Title or description matches `intern`, `internship`, `co-op`, `trainee`, `student worker`.
- **Junior / Entry-Level**:
  - Title matches: `junior`, `entry`, `new grad`, `[en]`, `graduate`, `associate`, `level 1`, `developer i`, `engineer i`.
  - Description matches: `entry level`, `new grad`, `0-1 year`, `0-2 years`, `1+ years exp`, `0+ years exp`.
- **Senior**: Matches `senior`, `sr`, `sr.`, `[se]`.
- **Lead**: Matches `staff`, `principal`, `lead`, `director`, `head`.
- **Mid**: Default technical baseline.

### 5.2 Fast Regex Pre-filter Safeguards
Located in `apps/analyzer/prefilter.py`:
- Rejects non-technical corporate noise (accounting, sales, marketing, generic recruiters, administrative roles).
- **CRITICAL EXEMPTION**: Must **never** reject legitimate AI engineering sub-disciplines such as:
  - `AI Trainer`, `LLM Trainer` (RLHF / Model Alignment)
  - `AI Evaluation`, `Model Evaluation` (Benchmarking & LLM-as-a-judge)
  - `Data Science Intern`, `AI Research Co-op`
