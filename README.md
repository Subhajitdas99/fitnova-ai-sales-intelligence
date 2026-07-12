# 🚀 FitNova AI Sales Intelligence

> Production-ready AI Sales Call Intelligence Platform built with **FastAPI**, **Clean Architecture**, **Whisper**, **WhisperX**, **OpenRouter**, **SQLAlchemy**, and **Streamlit**.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

# 📖 Overview

FitNova AI Sales Intelligence is an end-to-end AI platform for analyzing customer sales calls.

The platform automatically:

- Uploads sales call recordings
- Transcribes speech using Whisper
- Performs speaker diarization using WhisperX
- Generates AI-powered sales insights
- Scores sales conversations
- Produces coaching recommendations
- Displays interactive dashboards
- Stores results for future analytics

The backend follows **Clean Architecture** with clear separation between API, Application, Domain, and Infrastructure layers.

---

# ✨ Features

## 🎙 Audio Processing

- Upload MP3, WAV, M4A, MP4, MPEG and OGG recordings
- Background processing
- Whisper speech-to-text transcription
- WhisperX speaker diarization
- Automatic language detection
- Local audio storage

---

## 🤖 AI Sales Intelligence

- Executive summaries
- AI-generated coaching notes
- Sales scorecards
- Evidence extraction
- Customer sentiment analysis
- Follow-up recommendations
- Action items
- Confidence scoring

Supported AI providers:

- OpenRouter
- OpenAI
- Heuristic (offline mode)

---

## 📊 Interactive Dashboard

Built with Streamlit.

Features include:

- Executive Dashboard
- Advisor Performance
- AI Coaching
- Sales Analytics
- Recent Calls
- Transcript Viewer
- Call Details
- KPI Monitoring

---

## 🏗 Backend

- FastAPI REST API
- Clean Architecture
- Repository Pattern
- Dependency Injection
- SQLAlchemy ORM
- Background Tasks
- Pydantic Validation
- Structured JSON Logging
- Global Exception Handling
- Middleware Pipeline

---

## 🔒 Production Features

- Docker & Docker Compose
- GitHub Actions CI
- Health Checks
- Request Timeout Middleware
- Security Headers
- Request ID Tracking
- Startup Validation
- Environment-based Configuration

---

# 🏛 Architecture

```
                Streamlit Dashboard
                        │
                        ▼
                 FastAPI REST API
                        │
     ┌──────────────────┴──────────────────┐
     │                                     │
     ▼                                     ▼
Application Services             Background Tasks
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

• Whisper
• WhisperX
• OpenRouter
• OpenAI
• Heuristic
```

Project layout:

```
backend/
│
├── app/
│   ├── api/
│   ├── application/
│   ├── core/
│   ├── domain/
│   ├── infrastructure/
│   └── schemas/
│
├── main.py
│
frontend/
│   ├── components/
│   └── services/
│
docs/
tests/
```

---

# 🛠 Technology Stack

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

## Quality

- Pytest
- Ruff
- Black

---

# ⚙ Installation

Clone the repository.

```bash
git clone https://github.com/Subhajitdas99/fitnova-ai-sales-intelligence.git

cd fitnova-ai-sales-intelligence
```

Create a virtual environment.

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

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Configuration

Create a local environment file.

```bash
copy .env.example .env
```

Example configuration:

```env
FITNOVA_TRANSCRIPTION_PROVIDER=whisper
FITNOVA_DIARIZATION_PROVIDER=whisperx
FITNOVA_ANALYSIS_PROVIDER=openrouter
```

Some providers require credentials:

| Variable | Purpose |
|----------|---------|
| OPENROUTER_API_KEY | OpenRouter AI analysis |
| FITNOVA_OPENAI_API_KEY | OpenAI analysis |
| FITNOVA_HUGGINGFACE_AUTH_TOKEN | WhisperX speaker diarization |

---

# ▶ Running the Application

Start the backend.

```bash
uvicorn backend.main:app --reload
```

Start the frontend.

```bash
python -m streamlit run frontend/app.py
```

Open:

Backend

```
http://localhost:8000
```

Swagger UI

```
http://localhost:8000/docs
```

Frontend

```
http://localhost:8501
```

---

# 🐳 Docker

Build and start the application.

```bash
docker compose up --build
```

Stop.

```bash
docker compose down
```

---

# 📡 API Endpoints

## Health

```
GET /api/v1/health
```

## Calls

```
POST /api/v1/calls/upload

GET /api/v1/calls

GET /api/v1/calls/{call_id}

POST /api/v1/calls/{call_id}/process
```

## Dashboard

```
GET /api/v1/dashboard/overview

GET /api/v1/dashboard/executive

GET /api/v1/dashboard/advisors

GET /api/v1/dashboard/coaching
```

## Analytics

```
GET /api/v1/analytics
```

---

# 🧪 Testing

Run the complete test suite.

```bash
pytest -q
```

Check formatting.

```bash
black --check .
```

Run linting.

```bash
ruff check .
```

Verify Python compilation.

```bash
python -m compileall backend frontend
```

Current project status:

```
✓ 42/42 tests passing
✓ Black formatting passes
✓ Ruff lint passes
✓ Python compilation passes
```

---

# 📚 Documentation

Additional documentation:

- docs/configuration.md
- docs/deployment.md
- docs/logging.md
- docs/sprint7-analytics-architecture.md

---

# 🚀 Future Improvements

- PostgreSQL deployment
- Redis task queue
- Celery workers
- Authentication & Authorization
- Multi-tenant organizations
- Object storage (AWS S3 / Azure Blob)
- Real-time dashboard updates
- Kubernetes deployment
- Prometheus metrics
- Grafana dashboards

---

# 👨‍💻 Author

**Subhajit Das**

B.Tech Computer Science Engineering (AI & ML)

Machine Learning • Generative AI • Backend Engineering • MLOps

GitHub:

https://github.com/Subhajitdas99

---

# 📄 License

This project is licensed under the MIT License.
