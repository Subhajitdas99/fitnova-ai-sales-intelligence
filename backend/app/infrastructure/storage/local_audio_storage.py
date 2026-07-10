import shutil
from pathlib import Path
from typing import BinaryIO

from backend.app.application.interfaces.services import AudioStorageProtocol


class LocalAudioStorage(AudioStorageProtocol):
    """Filesystem-backed storage adapter for uploaded audio files."""

    def __init__(self, root_directory: Path) -> None:
        self._root_directory = root_directory
        self._root_directory.mkdir(parents=True, exist_ok=True)

    def save(self, source: BinaryIO, destination_name: str) -> Path:
        destination = self._root_directory / destination_name
        if hasattr(source, "seek"):
            source.seek(0)
        with destination.open("wb") as output_file:
            shutil.copyfileobj(source, output_file)
        return destination
