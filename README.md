# 🚀 FitNova AI Sales Intelligence

> A production-ready AI Sales Call Intelligence platform built with **FastAPI**, **Clean Architecture**, **Whisper**, **WhisperX**, **OpenRouter**, **SQLAlchemy**, and **Streamlit**.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

# 📖 Overview

FitNova AI Sales Intelligence is an end-to-end AI platform for analyzing sales calls.

The platform automatically:

- Uploads customer call recordings
- Transcribes speech into text
- Performs speaker diarization
- Generates AI-powered sales insights
- Scores sales performance
- Produces coaching recommendations
- Displays analytics dashboards
- Stores results for future reporting

The project is designed using **Clean Architecture** and follows modern backend engineering practices suitable for production systems.

---

# ✨ Features

## 🎙 Audio Processing

- Upload MP3/WAV/M4A recordings
- Local audio storage
- Background processing
- Whisper transcription
- WhisperX speaker diarization
- Automatic language detection

---

## 🤖 AI Sales Intelligence

- Executive summaries
- Sales scoring
- Category-wise scorecards
- Evidence extraction
- Customer sentiment
- Action items
- Coaching recommendations
- Confidence scoring

Supports multiple AI providers:

- OpenRouter
- OpenAI
- Heuristic (offline mode)

---

## 📊 Analytics Dashboard

Interactive Streamlit dashboard including:

- Recent Calls
- KPI Overview
- Performance Trends
- Executive Summary
- Coaching Dashboard
- Sales Analytics
- Call Details
- Transcript Viewer

---

## 🏗 Backend Features

- FastAPI REST API
- Clean Architecture
- Repository Pattern
- Dependency Injection
- SQLAlchemy ORM
- Background Tasks
- Pydantic Validation
- Global Exception Handling
- Request Middleware
- Structured JSON Logging

---

## 🔒 Production Features

- Docker support
- Docker Compose
- Health Checks
- Request Timeout Middleware
- Security Headers
- Request ID Tracking
- Startup Validation
- GitHub Actions CI
- Environment-based Configuration

---

# 🏛 Architecture

```
                    Streamlit Dashboard
                            │
                            ▼
                     FastAPI REST API
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
 Application Services                 Background Tasks
        │
        ▼
 Repository Layer
        │
        ▼
 SQLAlchemy ORM
        │
        ▼
 SQLite / PostgreSQL

        AI Providers

 Whisper
 WhisperX
 OpenRouter
 OpenAI
 Heuristic
```

The backend follows **Clean Architecture**.

```
backend/
│
├── api/
├── application/
├── domain/
├── infrastructure/
├── schemas/
└── core/
```

---

# 🛠 Tech Stack

## Backend

- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- Uvicorn

## AI

- Whisper
- WhisperX
- OpenRouter
- OpenAI

## Frontend

- Streamlit
- Plotly

## DevOps

- Docker
- Docker Compose
- GitHub Actions

## Testing

- Pytest
- Ruff
- Black

---

# 📂 Repository Structure

```
FitNova/
│
├── backend/
│   ├── api/
│   ├── application/
│   ├── core/
│   ├── domain/
│   ├── infrastructure/
│   └── schemas/
│
├── frontend/
│   ├── components/
│   └── services/
│
├── docs/
│
├── tests/
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Subhajitdas99/fitnova-ai-sales-intelligence.git

cd fitnova-ai-sales-intelligence
```

Create a virtual environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Configuration

Create a local environment file

```bash
copy .env.example .env
```

Configure your preferred providers.

Example:

```
FITNOVA_TRANSCRIPTION_PROVIDER=whisper

FITNOVA_DIARIZATION_PROVIDER=whisperx

FITNOVA_ANALYSIS_PROVIDER=openrouter
```

---

# ▶ Running the Application

Start the backend

```bash
uvicorn backend.main:app --reload
```

Start the frontend

```bash
streamlit run frontend/app.py
```

---

# 🐳 Docker

Build and start all services

```bash
docker compose up --build
```

Stop

```bash
docker compose down
```

---

# 📡 API Endpoints

## Health

```
GET /api/v1/health
```

---

## Calls

```
POST /api/v1/calls/upload

GET /api/v1/calls

GET /api/v1/calls/{call_id}

POST /api/v1/calls/{call_id}/process
```

---

## Dashboard

```
GET /api/v1/dashboard/overview

GET /api/v1/dashboard/analytics
```

---

# 🧪 Testing

Run all tests

```bash
pytest -q
```

Format check

```bash
black --check .
```

Lint

```bash
ruff check .
```

Compilation

```bash
python -m compileall backend frontend
```

Current Status

```
42 / 42 tests passing
```

---

# 📚 Documentation

Additional documentation is available in:

- `docs/architecture.md`
- `docs/deployment.md`
- `docs/configuration.md`
- `docs/logging.md`
- `docs/sprint7-analytics-architecture.md`

---

# 🚀 Future Improvements

- PostgreSQL production deployment
- Redis task queue
- Celery workers
- Authentication & Authorization
- Multi-tenant organizations
- S3/Azure Blob Storage
- Real-time dashboard updates
- Kubernetes deployment
- Prometheus metrics
- Grafana dashboards

---

# 👨‍💻 Author

**Subhajit Das**

B.Tech CSE (AI & ML)

Machine Learning • Generative AI • Backend Engineering • MLOps

GitHub:

https://github.com/Subhajitdas99

---

# 📄 License

This project is licensed under the MIT License.
