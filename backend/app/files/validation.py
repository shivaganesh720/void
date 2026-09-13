from dataclasses import dataclass
from pathlib import PurePath


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@dataclass(frozen=True)
class FileMetadata:
    filename: str
    content_type: str
    size: int


def validate_upload(metadata: FileMetadata, max_bytes: int) -> None:
    name = PurePath(metadata.filename).name
    extension = PurePath(name).suffix.casefold()
    if name != metadata.filename or not name or name in {".", ".."}:
        raise ValueError("INVALID_FILE: unsafe filename")
    if metadata.size <= 0:
        raise ValueError("EMPTY_DOCUMENT: file is empty")
    if metadata.size > max_bytes:
        raise ValueError("FILE_TOO_LARGE: upload exceeds the configured limit")
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("UNSUPPORTED_FILE_TYPE: supported formats are PDF, DOCX, TXT, and Markdown")
    if metadata.content_type in {"application/x-msdownload", "application/x-sh", "application/x-executable"}:
        raise ValueError("INVALID_FILE: executable content is not accepted")