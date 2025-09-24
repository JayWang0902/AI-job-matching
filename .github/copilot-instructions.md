# Copilot Instructions for AI Job Matching

## Project Overview
- **Purpose:** AI-powered job matching platform with user authentication, resume upload/parsing, job scraping, and AI-driven job-candidate matching.
- **Core stack:** FastAPI, SQLAlchemy, Celery, PostgreSQL/SQLite, S3, OpenAI API, pgvector for embeddings.
- **Key flows:**
  - Users register/login (JWT auth), upload resumes (S3), resumes are parsed and embedded.
  - Jobs are scraped from external sources, embedded, and stored.
  - Matching runs daily (Celery), comparing resume/job embeddings, storing top matches with AI-generated analysis.

## Architecture & Key Components
- `app/api/`: FastAPI routers for `auth`, `resume`, `matches` endpoints. All business logic is in `services/`.
- `app/services/`: Core business logic:
  - `job_matching_service.py`: Vector search & OpenAI analysis for job-candidate matching.
  - `job_scraper_service.py` & `job_scrapers/`: Scrape/normalize jobs from sources.
  - `resume_processing_service.py`: Download, parse, and embed resumes.
  - `s3_service.py`: S3 upload/download, presigned URLs.
- `app/models/`: SQLAlchemy models for User, Resume, Job, JobMatch.
- `app/tasks.py`: Celery tasks for scraping, matching, and daily orchestration.
- `app/main.py`: FastAPI app, includes routers, CORS, health/debug endpoints.

## Developer Workflows

### Local (non-Docker)
- **Initialize DB:**
  ```bash
  python init_db.py
  ```
- **Run API locally:**
  ```bash
  uvicorn app.main:app --reload
  ```
- **Run Celery worker:**
  ```bash
  celery -A app.celery_app.celery_app worker --loglevel=info
  ```

### Docker-based
- **Build and run services (API, Celery, Redis):**
  ```bash
  docker-compose up --build
  ```
- **Run in detached mode:**
  ```bash
  docker-compose up -d
  ```
- **Stop services:**
  ```bash
  docker-compose down
  ```

### Common Tasks
- **Trigger daily flow (scrape+match):**
  - Manually via API: `POST /debug/trigger-daily-flow`
  - Or call the Celery task directly: `run_daily_flow`
- **Test user system:**
  ```bash
  python test_user_system.py
  ```

## Project Conventions & Patterns
- **Celery Orchestration:** The main daily task is `run_daily_flow` in `app/tasks.py`. It uses a chain to first execute `scrape_all_jobs` and then, upon completion, triggers `trigger_matching_for_all_users`. This second task fetches all active users and creates a parallel group of `match_jobs_for_user` tasks. This ensures scraping completes before matching begins.
- **Embeddings:** All matching is via pgvector (1536-dim vectors from OpenAI's `text-embedding-ada-002`) on both jobs and resumes.
- **AI analysis:** OpenAI API (see `openai_service.py`) generates match explanations, not just scores.
- **Resume upload:** Always via presigned S3 URLs (`/resume/upload-url`), then update status (`/resume/{id}/status`).
- **Job scraping:** Add new scrapers in `services/job_scrapers/`, register in `SCRAPERS` list in `job_scraper_service.py`.
- **Configuration:** All secrets and environment-specific settings (DB URLs, API keys) are managed via a `.env` file, as shown in `docker-compose.yml`.
- **Security:** JWT auth is required for most endpoints. User data is isolated.

## Integration Points
- **S3:** For all resume files. Configure via env vars (`S3_BUCKET_NAME`, etc).
- **OpenAI:** For embeddings and match analysis. Requires `OPENAI_API_KEY`.
- **pgvector:** Used for vector search in job/resume matching. Assumes a PostgreSQL DB with the pgvector extension enabled.
- **Redis:** Used as the Celery message broker.

## Tips for AI Agents
- Always use the service layer for business logic, not direct DB/model access in API routers.
- When adding new endpoints, follow the pattern in `app/api/` and use FastAPI's dependency injection for DB sessions and authenticated users.
- For new batch/background flows, prefer creating Celery tasks and orchestrate them via `app/tasks.py`.
- Use logging for all error/exception paths, especially in async/background jobs.

---
For questions about unclear conventions or missing documentation, ask for clarification or check the latest code in `app/services/` and `app/tasks.py`.
