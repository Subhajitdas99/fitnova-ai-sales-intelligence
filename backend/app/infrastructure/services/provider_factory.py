from backend.app.core.config import Settings
from backend.app.application.interfaces.services import (
    CallIntelligenceServiceProtocol,
    DiarizationServiceProtocol,
    TranscriptionServiceProtocol,
)
from backend.app.infrastructure.services.heuristic_call_intelligence_service import (
    HeuristicCallIntelligenceService,
)
from backend.app.infrastructure.services.heuristic_diarization_service import (
    HeuristicDiarizationService,
)
from backend.app.infrastructure.services.openai_call_intelligence_service import (
    OpenAICallIntelligenceService,
)
from backend.app.infrastructure.services.openrouter_call_intelligence_service import (
    OpenRouterCallIntelligenceService,
)
from backend.app.infrastructure.services.whisper_transcription_service import (
    WhisperTranscriptionService,
)
from backend.app.infrastructure.services.whisperx_diarization_service import (
    WhisperXDiarizationService,
)


def build_transcription_service(settings: Settings) -> TranscriptionServiceProtocol:
    return WhisperTranscriptionService(
        model_size=settings.whisper_model_size,
        device=settings.whisper_device,
        retry_attempts=settings.transcription_retry_attempts,
        retry_delay_seconds=settings.transcription_retry_delay_seconds,
        temperature=settings.whisper_temperature,
    )


def build_diarization_service(settings: Settings) -> DiarizationServiceProtocol:
    if settings.diarization_provider == "whisperx":
        return WhisperXDiarizationService(
            huggingface_auth_token=settings.huggingface_auth_token,
            device=settings.whisperx_device,
        )
    return HeuristicDiarizationService()


def build_call_intelligence_service(
    settings: Settings,
) -> CallIntelligenceServiceProtocol:
    if settings.analysis_provider == "openrouter":
        from backend.app.application.services.prompt_builder import PromptBuilder

        return OpenRouterCallIntelligenceService(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            prompt_builder=PromptBuilder(),
        )
    if settings.analysis_provider == "openai":
        return OpenAICallIntelligenceService(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
    return HeuristicCallIntelligenceService()
