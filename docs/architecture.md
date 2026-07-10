# FitNova AI Sales Intelligence Architecture

## 1. Architectural Style

The codebase follows a Clean Architecture inspired layout:

- `backend/app/api`
  Reason: isolates HTTP concerns, request validation, routing, and response serialization.
- `backend/app/application`
  Reason: owns use cases such as uploading calls, processing calls, and composing dashboard analytics.
- `backend/app/domain`
  Reason: keeps business language explicit through enums and entities like `TranscriptSegment`, `ActionItem`, and `CallAnalysis`.
- `backend/app/infrastructure`
  Reason: contains adapters for SQLAlchemy, local file storage, and AI providers so business logic does not depend on vendor-specific details.
- `frontend`
  Reason: separates the operator-facing dashboard from backend API logic while keeping it lightweight for the internship scope.

This structure was chosen because the platform will grow in multiple directions at once: ingestion, AI orchestration, analytics, and UI. A layered design reduces coupling and makes it safer to replace SQLite with PostgreSQL, mock providers with real AI models, and Streamlit with another frontend later if needed.

## 2. Why Repository and Service Boundaries Exist

- `CallRepositoryProtocol`
  Reason: abstracts persistence so application services are not bound to SQLAlchemy details.
- `AudioStorageProtocol`
  Reason: allows the local filesystem to be replaced later with S3, Azure Blob Storage, or GCS.
- `TranscriptionServiceProtocol`
  Reason: keeps Whisper optional and swappable.
- `DiarizationServiceProtocol`
  Reason: lets WhisperX or pyannote-style speaker separation be added without rewriting use cases.
- `CallIntelligenceServiceProtocol`
  Reason: separates core workflow orchestration from LLM-specific prompting logic.

These boundaries follow SOLID, especially dependency inversion and single responsibility.

## 3. Data Model Decisions

### `CallRecordModel`

This is the aggregate root for a sales call because nearly every product view starts with the call as the central entity.

It stores:

- operational fields such as file names, status, failure reason, and timestamps
- analytics fields such as sentiment, outcome, close probability, talk ratios, and objection count
- JSON lists for objections, products discussed, and key topics

Reason: this provides a single query-friendly summary row that is easy to expose in dashboards.

### `TranscriptSegmentModel`

Transcript segments are stored in a separate table.

Reason: transcripts are naturally one-to-many data, and separating them avoids bloating the main call row while preserving detailed drill-down.

### `ActionItemModel`

Action items are also separated.

Reason: they are actionable business outputs that may later need assignment workflows, due-date logic, or export to CRMs and task systems.

## 4. Background Processing Decision

Uploads return immediately with a `202 Accepted` response, and processing runs in a FastAPI background task.

Reason:

- the UI stays responsive
- long-running AI tasks do not block the request
- call status becomes explicit: `queued`, `processing`, `completed`, `failed`

For a larger deployment, this background step should move to a dedicated worker queue such as Celery, Dramatiq, or RQ, but the current structure already isolates the orchestration logic so that migration is straightforward.

## 5. Provider Selection Strategy

The system is config-driven:

- local development defaults to `mock` and `heuristic` providers
- production-style behavior can switch to `whisper`, `whisperx`, and `openai`

Reason: a runnable default is essential for developer productivity and evaluation, while real providers remain available through the same interfaces.

## 6. Why SQLite First and PostgreSQL Compatibility Later Works

SQLAlchemy models intentionally avoid SQLite-only design choices.

Reason:

- column types are standard and portable
- relationships are explicit
- JSON fields are supported in both SQLite and PostgreSQL through SQLAlchemy abstractions

This means the later migration primarily affects infrastructure configuration rather than application logic.

## 7. Validation, Logging, and Error Handling Choices

- Pydantic schemas validate and serialize API contracts
  Reason: keeps request and response boundaries strict and typed.
- Central application exceptions model domain and infrastructure failures
  Reason: routes stay clean and error handling remains predictable.
- Application-wide logging is configured once in the app bootstrap
  Reason: every service and background task gets consistent operational logs.

## 8. Frontend Design Decisions

The Streamlit app is split into:

- `services/api_client.py`
  Reason: all HTTP logic lives in one place.
- `components/metrics.py`, `components/charts.py`, `components/tables.py`, `components/detail.py`
  Reason: the dashboard remains composable and easier to extend.

This avoids the common internship-project anti-pattern where the UI becomes a single unmaintainable script.

## 9. Production Readiness Tradeoffs

What is production-minded now:

- strong folder structure
- explicit use cases
- typed models and schemas
- modular adapters
- background processing lifecycle
- Docker support
- analytics-ready persistence

What should be the next production steps:

1. Add Alembic migrations instead of relying on `create_all`.
2. Introduce a worker queue for heavy AI jobs.
3. Add authentication and role-based access control.
4. Add automated tests for services and API routes.
5. Add object storage and signed URLs for audio.
6. Add observability with structured logs and metrics.

These are next because they strengthen scale and operability without requiring a redesign of the current code.
