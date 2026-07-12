# FitNova AI Sales Intelligence - Deployment Manual

This document provides guidelines for deploying the FitNova application in staging and production environments.

## 1. Containerization & Architecture

FitNova is containerized using a multi-stage Docker build process designed for efficiency and safety.
Both services run under a non-root system user (`fitnova`) to adhere to the principle of least privilege.

- **Backend**: Python 3.12-slim base image. Packages are compiled and isolated inside a virtual environment (`/opt/venv`). Audio uploads are persisted inside a mapped storage volume under `/app/backend/storage`.
- **Frontend**: Lightweight Streamlit-based UI runner under Python 3.12-slim. Communicates with the Backend API.

## 2. Docker Compose Deployment

We use Docker Compose to manage and orchestrate the service stack.

### Production Docker Compose configuration:

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: fitnova-backend
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - backend_storage:/app/backend/storage
      - ./backend:/app/backend
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3)"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: fitnova-frontend
    environment:
      BACKEND_URL: http://backend:8000
    ports:
      - "8501:8501"
    volumes:
      - ./frontend:/app/frontend
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped

volumes:
  backend_storage:
```

### Steps to Run:

1. **Configure Environment Variables**:
   Create a `.env` file from the provided `.env.example` in the project root:
   ```bash
   cp .env.example .env
   # Edit .env with production credentials (API keys, environments, etc.)
   ```

2. **Build and Run**:
   Start the services in detached mode:
   ```bash
   docker compose up --build -d
   ```

3. **Check Container Status**:
   Confirm that both containers are running and healthy:
   ```bash
   docker compose ps
   ```

## 3. Storage Mounting & Data Persistence

- The database file (e.g. SQLite database) and audio files require persistent storage.
- By default, SQLite stores data under `./backend/fitnova_ai.db`. Ensure that the database file path is mapped to a volume or configured at a persistent path like `/app/backend/storage/fitnova_ai.db` in production by setting the `FITNOVA_DATABASE_URL` env variable.
- In Docker Compose, the named volume `backend_storage` maps directly to `/app/backend/storage` to store audio files permanently.

## 4. Health Checks & Reliability

Both containers expose built-in health indicators:
- **Backend Healthcheck**: Uses `urllib.request` to query `/health/live` internally every 30 seconds.
- **Frontend Healthcheck**: Uses `urllib.request` to query Streamlit's internal health endpoint `/_stcore/health`.
- In Compose, the frontend service delays startup until the backend container returns a successful `healthy` status code.
