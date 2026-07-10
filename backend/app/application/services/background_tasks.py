import logging

from backend.app.api.dependencies.services import (
    get_call_intelligence_service,
    get_diarization_service,
    get_transcription_service,
)
from backend.app.application.services.call_processing_service import CallProcessingService
from backend.app.infrastructure.database.session import session_scope
from backend.app.infrastructure.repositories.call_repository import CallRepository


logger = logging.getLogger(__name__)


def process_call_in_background(call_id: str) -> None:
    """Run the sales-call processing pipeline in a background task."""

    with session_scope() as db:
        repository = CallRepository(db)
        service = CallProcessingService(
            repository=repository,
            transcription_service=get_transcription_service(),
            diarization_service=get_diarization_service(),
            intelligence_service=get_call_intelligence_service(),
        )
        service.process_call(call_id)
        logger.info("Background job finished for call %s", call_id)
