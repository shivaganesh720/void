from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree

from app.files.validation import FileMetadata, validate_upload


@dataclass(frozen=True)
class ParsedDocument:
    source_type: str
    file_name: str
    extracted_text: str
    character_count: int
    parsing_status: str
    warnings: tuple[str, ...] = ()
    pages: tuple[dict, ...] = ()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _docx_text(data: bytes) -> str:
    try:
        with ZipFile(BytesIO(data)) as archive:
            xml = archive.read("word/document.xml")
    except (BadZipFile, KeyError) as exc:
        raise ValueError("DOCUMENT_PARSE_FAILED: invalid DOCX archive") from exc
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise ValueError("DOCUMENT_PARSE_FAILED: invalid DOCX XML") from exc
    return " ".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))


def _pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        return "\n".join(_normalize(page.extract_text() or "") for page in reader.pages)
    except ImportError as exc:
        raise ValueError("DOCUMENT_PARSE_FAILED: PDF support is not installed") from exc
    except Exception as exc:
        raise ValueError("DOCUMENT_PARSE_FAILED: PDF text extraction failed") from exc


def parse_document(filename: str, content_type: str, data: bytes, source_type: str, max_bytes: int) -> ParsedDocument:
    validate_upload(FileMetadata(filename, content_type, len(data)), max_bytes)
    extension = filename.rsplit(".", 1)[-1].casefold()
    try:
        text = _pdf_text(data) if extension == "pdf" else _docx_text(data) if extension == "docx" else data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("DOCUMENT_PARSE_FAILED: document is not valid UTF-8") from exc
    text = _normalize(text)
    if not text:
        raise ValueError("EMPTY_DOCUMENT: no readable text was extracted")
    warning = ("PAGE_AND_SECTION_METADATA_UNAVAILABLE",) if extension in {"txt", "md"} else ()
    return ParsedDocument(source_type, filename, text, len(text), "SUCCEEDED", warning, ({"page_number": 1, "text": text},))