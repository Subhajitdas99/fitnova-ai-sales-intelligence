# FitNova AI Sales Intelligence - Configuration Manual

This document outlines the configuration options, environment variables, validation rules, and provider settings for the FitNova application.

## 1. Setting Environment Variables

The backend application is built using Pydantic Settings, loading configurations from environment variables prefixed with `FITNOVA_` (with fallback to non-prefixed variables for certain parameters like `OPENROUTER_API_KEY`).

### Core Configuration Groups

All configuration variables are declared in [config.py](file:///f:/fitnova-ai/backend/app/core/config.py).

#### 1. General Application Settings
- `FITNOVA_APP_NAME`: Title of the application (default: `"FitNova AI Sales Intelligence"`).
- `FITNOVA_APP_VERSION`: Current version identifier.
- `FITNOVA_ENVIRONMENT`: Deployment environment (e.g. `"production"`, `"staging"`, `"development"`, `"test"`).
- `FITNOVA_DEBUG`: Boolean to turn on debug mode (defaults to `False`).
- `FITNOVA_LOG_LEVEL`: Log level limit (`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`).

#### 2. Database & Storage Settings
- `FITNOVA_DATABASE_URL` (or `DATABASE_URL`): SQLAlchemy database connection string (e.g. `"sqlite:///./backend/fitnova_ai.db"`).
- `FITNOVA_UPLOAD_DIRECTORY` (or `UPLOAD_DIRECTORY`): Path to save uploaded audio files (defaults to `backend/storage/audio`).

#### 3. AI Providers & Model Settings
- `FITNOVA_TRANSCRIPTION_PROVIDER`: Chosen transcription client (default: `"whisper"`).
- `FITNOVA_DIARIZATION_PROVIDER`: Chosen diarization service (defaults to `"whisperx"`).
- `FITNOVA_ANALYSIS_PROVIDER`: Chosen LLM analyzer (defaults to `"openrouter"`).
- `OPENROUTER_API_KEY`: API credential for OpenRouter inference.
- `OPENROUTER_MODEL`: Model ID to request (default: `"openai/gpt-4.1-mini"`).
- `FITNOVA_OPENAI_API_KEY`: API credential for OpenAI (if used).
- `FITNOVA_OPENAI_MODEL`: Model ID to request (default: `"gpt-4.1-mini"`).

#### 4. Model Hyperparameters & Optimization
- `FITNOVA_WHISPER_MODEL_SIZE` (or `WHISPER_MODEL`): Whisper model size to load (default: `"base"`).
- `FITNOVA_WHISPER_DEVICE`: Execution device for Whisper (options: `"auto"`, `"cpu"`, `"cuda"`).
- `FITNOVA_WHISPER_TEMPERATURE`: Temperature parameter for speech decoding (default: `0.0`).
- `FITNOVA_WHISPERX_DEVICE`: Execution device for WhisperX (options: `"cpu"`, `"cuda"`).
- `FITNOVA_HUGGINGFACE_AUTH_TOKEN` (or `HUGGINGFACE_TOKEN`): Auth token for Pyannote diarization models.
- `FITNOVA_DEFAULT_LANGUAGE`: Transcription target language (default: `"auto"`).
- `FITNOVA_TRANSCRIPTION_RETRY_ATTEMPTS`: Number of retries for API requests (default: `3`).
- `FITNOVA_TRANSCRIPTION_RETRY_DELAY_SECONDS`: Delay between retries (default: `2.0`).

## 2. Startup Validation Logic

At container boot or backend application startup, configuration constraints are validated by calling the `validate_for_startup()` method:

- **Strict Validation**: If `FITNOVA_ENVIRONMENT` is set to `"staging"` or `"production"`, or `strict_startup_validation` is explicitly enabled:
  - If the chosen `FITNOVA_ANALYSIS_PROVIDER` is `"openrouter"`, `OPENROUTER_API_KEY` must be configured.
  - If the validation fails, a `StartupConfigurationError` is raised, preventing the application from starting.
- **Development/Local Mode**: In `"local"`, `"development"`, or `"test"` environments, missing keys will only log warnings rather than crashing startup.
