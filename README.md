# FitNova AI Sales Intelligence

FitNova AI Sales Intelligence is a production-minded AI sales call intelligence platform built with FastAPI, SQLAlchemy, SQLite, Streamlit, Plotly, and extensible AI provider adapters for Whisper, WhisperX, and OpenAI.

## What This Version Delivers

- Clean Architecture inspired backend with separated API, application, domain, and infrastructure layers
- Sales-call upload workflow with file validation and local audio storage
- Background processing pipeline for transcription, diarization, and call intelligence generation
- SQLite persistence with PostgreSQL-friendly SQLAlchemy models
- Analytics APIs for recent calls and dashboard KPIs
- Modular Streamlit dashboard for uploads, KPI monitoring, charts, and call detail inspection
- Dockerized backend and frontend services
- Config-driven provider switching between runnable local heuristics and production AI adapters

## Quick Start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy the environment file and adjust providers as needed:

```bash
copy .env.example .env
```

3. Start the backend API:

```bash
uvicorn backend.main:app --reload
```

4. Start the Streamlit dashboard in a second terminal:

```bash
streamlit run frontend/app.py
```

5. Open the product surfaces:

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Dashboard: [http://localhost:8501](http://localhost:8501)

## Docker Workflow

```bash
docker compose up --build
```

## Architecture

Detailed design decisions are documented in [docs/architecture.md](/F:/fitnova-ai/docs/architecture.md).

## Provider Strategy

The default configuration uses:

- `mock` transcription
- `heuristic` diarization
- `heuristic` call analysis

That keeps the platform runnable without heavyweight ML downloads during development. For production-like AI behavior, switch providers through environment variables:

- `FITNOVA_TRANSCRIPTION_PROVIDER=whisper`
- `FITNOVA_DIARIZATION_PROVIDER=whisperx`
- `FITNOVA_ANALYSIS_PROVIDER=openai`

## Core API Endpoints

- `GET /api/v1/health/`
- `POST /api/v1/calls/upload`
- `GET /api/v1/calls`
- `GET /api/v1/calls/{call_id}`
- `POST /api/v1/calls/{call_id}/process`
- `GET /api/v1/dashboard/overview`
