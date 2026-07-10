from dataclasses import dataclass


@dataclass(slots=True)
class CallCreationData:
    """Command object for creating a new sales call record."""

    call_id: str
    original_file_name: str
    stored_file_name: str
    audio_path: str
    customer_name: str
    sales_rep_name: str
    language: str
    notes: str | None = None
