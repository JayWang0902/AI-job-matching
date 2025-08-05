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
- **Run API locally:**
  ```bash
  uvicorn app.main:app --reload
  ```
- **Initialize DB:**
  ```bash
  python init_db.py
  ```
- **Run Celery worker:**
  ```bash
  celery -A app.celery_app.celery_app worker --loglevel=info
  ```
- **Trigger daily flow (scrape+match):**
  - Manually: `POST /debug/trigger-daily-flow` or call `run_daily_flow` Celery task.
- **Test user system:**
  ```bash
  python test_user_system.py
  ```

## Project Conventions & Patterns
- **Embeddings:** All matching is via pgvector (1536-dim vectors) on both jobs and resumes.
- **AI analysis:** OpenAI API (see `openai_service.py`) generates match explanations, not just scores.
- **Resume upload:** Always via presigned S3 URLs (`/resume/upload-url`), then update status (`/resume/{id}/status`).
- **Job scraping:** Add new scrapers in `services/job_scrapers/`, register in `job_scraper_service.py`.
- **Celery orchestration:** All batch/daily flows are Celery tasks, not HTTP endpoints.
- **Error handling:** Use logging, propagate exceptions for Celery/AI failures.
- **Security:** JWT auth everywhere, user isolation for all resume/match/job data.

## Integration Points
- **S3:** For all resume files. Configure via env vars (`S3_BUCKET_NAME`, etc).
- **OpenAI:** For embeddings and match analysis. Requires `OPENAI_API_KEY`.
- **pgvector:** Used for vector search in job/resume matching.

## Examples
- See `USER_SYSTEM_README.md` and `RESUME_UPLOAD_GUIDE.md` for API usage and integration details.
- Example: To add a new job source, implement a scraper in `services/job_scrapers/`, add to `SCRAPERS` in `job_scraper_service.py`.

## Tips for AI Agents
- Always use service layer for business logic, not direct DB/model access in API.
- When adding new endpoints, follow the pattern in `api/` and use dependency injection for DB/user.
- For new batch flows, prefer Celery tasks and orchestrate via `tasks.py`.
- Use logging for all error/exception paths, especially in async/background jobs.

---
For questions about unclear conventions or missing documentation, ask for clarification or check the latest code in `services/` and `models/`.
