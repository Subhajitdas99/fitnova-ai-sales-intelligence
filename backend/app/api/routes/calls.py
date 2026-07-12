import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from backend.app.api.dependencies.services import (
    get_call_repository,
    get_processing_service,
    get_upload_service,
)
from backend.app.application.services.background_tasks import process_call_in_background
from backend.app.application.services.call_processing_service import (
    CallProcessingService,
)
from backend.app.application.services.call_upload_service import CallUploadService
from backend.app.core.exceptions import ApplicationError, ResourceNotFoundError
from backend.app.domain.enums import CallStatus
from backend.app.infrastructure.repositories.call_repository import CallRepository
from backend.app.schemas.calls import (
    CallDetailResponse,
    CallListItemResponse,
    UploadCallResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.post(
    "/upload",
    response_model=UploadCallResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_call(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    customer_name: Annotated[str, Form(...)],
    sales_rep_name: Annotated[str, Form(...)],
    language: Annotated[str, Form()] = "auto",
    notes: Annotated[str | None, Form()] = None,
    upload_service: CallUploadService = Depends(get_upload_service),
) -> UploadCallResponse:
    file_contents = await file.read()
    file.file.seek(0)
    record = upload_service.create_call(
        file_name=file.filename or "uploaded_audio.wav",
        file_size_bytes=len(file_contents),
        file_stream=file.file,
        customer_name=customer_name,
        sales_rep_name=sales_rep_name,
        language=language,
        notes=notes,
    )
    background_tasks.add_task(process_call_in_background, record.id)

    return UploadCallResponse(
        id=record.id,
        status=CallStatus(record.status),
        original_file_name=record.original_file_name,
        message="Audio uploaded successfully. Processing has started in the background.",
    )


@router.get("/", response_model=list[CallListItemResponse])
def list_calls(
    status_filter: CallStatus | None = None,
    limit: int = 50,
    repository: CallRepository = Depends(get_call_repository),
) -> list[CallListItemResponse]:
    calls = repository.list_calls(status=status_filter, limit=limit)
    return [CallListItemResponse.model_validate(call) for call in calls]


@router.get("/{call_id}", response_model=CallDetailResponse)
def get_call(
    call_id: str,
    repository: CallRepository = Depends(get_call_repository),
) -> CallDetailResponse:
    record = repository.get_call(call_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Call not found."
        )
    return CallDetailResponse.model_validate(record)


@router.post("/{call_id}/process", response_model=CallDetailResponse)
def process_call_now(
    call_id: str,
    processing_service: CallProcessingService = Depends(get_processing_service),
    repository: CallRepository = Depends(get_call_repository),
) -> CallDetailResponse:
    try:
        processing_service.process_call(call_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ApplicationError as exc:
        logger.exception("Failed to process call %s", call_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    record = repository.get_call(call_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Call not found."
        )
    return CallDetailResponse.model_validate(record)
