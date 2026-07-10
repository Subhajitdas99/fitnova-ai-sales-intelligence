from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from backend.app.application.dto.call_context import CallCreationData
from backend.app.application.interfaces.call_repository import CallRepositoryProtocol
from backend.app.application.interfaces.services import AudioStorageProtocol
from backend.app.core.config import Settings
from backend.app.core.exceptions import DomainValidationError
from backend.app.infrastructure.database.models.call_record import CallRecordModel


class CallUploadService:
    """Handles validation and persistence for uploaded sales-call audio."""

    _allowed_extensions = {".mp3", ".wav", ".m4a", ".mp4", ".mpeg", ".ogg"}

    def __init__(
        self,
        repository: CallRepositoryProtocol,
        audio_storage: AudioStorageProtocol,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._audio_storage = audio_storage
        self._settings = settings

    def create_call(
        self,
        file_name: str,
        file_size_bytes: int,
        file_stream: BinaryIO,
        customer_name: str,
        sales_rep_name: str,
        language: str,
        notes: str | None = None,
    ) -> CallRecordModel:
        extension = Path(file_name).suffix.lower()
        if extension not in self._allowed_extensions:
            raise DomainValidationError(
                "Unsupported file type. Supported formats: mp3, wav, m4a, mp4, mpeg, ogg."
            )
        if file_size_bytes > self._settings.max_upload_size_bytes:
            raise DomainValidationError(
                f"File exceeds the {self._settings.max_upload_size_mb} MB upload limit."
            )
        normalized_language = self._normalize_language(language)

        call_id = str(uuid4())
        stored_file_name = f"{call_id}{extension}"
        audio_path = self._audio_storage.save(file_stream, stored_file_name)

        command = CallCreationData(
            call_id=call_id,
            original_file_name=file_name,
            stored_file_name=stored_file_name,
            audio_path=str(audio_path),
            customer_name=customer_name,
            sales_rep_name=sales_rep_name,
            language=normalized_language,
            notes=notes,
        )
        return self._repository.create_call(command)

    def _normalize_language(self, language: str) -> str:
        normalized = (language or self._settings.default_language).strip().lower()
        if normalized in {"", "auto", "detect", "auto-detect"}:
            return "auto"
        return normalized
