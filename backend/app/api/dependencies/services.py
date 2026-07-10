from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.application.services.call_processing_service import CallProcessingService
from backend.app.application.services.call_upload_service import CallUploadService
from backend.app.application.services.dashboard_service import DashboardService
from backend.app.core.config import Settings, get_settings
from backend.app.infrastructure.database.session import get_db
from backend.app.infrastructure.repositories.call_repository import CallRepository
from backend.app.infrastructure.services.provider_factory import (
    build_call_intelligence_service,
    build_diarization_service,
    build_transcription_service,
)
from backend.app.infrastructure.storage.local_audio_storage import LocalAudioStorage


def get_call_repository(db: Session = Depends(get_db)) -> CallRepository:
    return CallRepository(db)


def get_audio_storage(settings: Settings = Depends(get_settings)) -> LocalAudioStorage:
    return LocalAudioStorage(settings.normalized_storage_dir)


@lru_cache
def get_transcription_service():
    return build_transcription_service(get_settings())


@lru_cache
def get_diarization_service():
    return build_diarization_service(get_settings())


@lru_cache
def get_call_intelligence_service():
    return build_call_intelligence_service(get_settings())


def get_upload_service(
    repository: CallRepository = Depends(get_call_repository),
    audio_storage: LocalAudioStorage = Depends(get_audio_storage),
    settings: Settings = Depends(get_settings),
) -> CallUploadService:
    return CallUploadService(repository, audio_storage, settings)


def get_processing_service(
    repository: CallRepository = Depends(get_call_repository),
    transcription_service=Depends(get_transcription_service),
    diarization_service=Depends(get_diarization_service),
    intelligence_service=Depends(get_call_intelligence_service),
) -> CallProcessingService:
    return CallProcessingService(
        repository=repository,
        transcription_service=transcription_service,
        diarization_service=diarization_service,
        intelligence_service=intelligence_service,
    )


def get_dashboard_service(
    repository: CallRepository = Depends(get_call_repository),
) -> DashboardService:
    return DashboardService(repository)
