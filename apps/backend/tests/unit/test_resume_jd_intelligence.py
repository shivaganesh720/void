from io import BytesIO
from zipfile import ZipFile

import pytest

from app.utils.text import parse_document
from app.main import app
from app.capabilities.resume_jd.parser import build_analysis, validate_analysis


def test_docx_text_is_extracted_and_normalized() -> None:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", "<document xmlns='x'><body><p><t>Python SQL</t></p></body></document>")
    parsed = parse_document("resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", buffer.getvalue(), "RESUME", 10000)
    assert parsed.extracted_text == "Python SQL"
    assert parsed.source_type == "RESUME"


def test_empty_and_unsupported_documents_fail_clearly() -> None:
    with pytest.raises(ValueError, match="EMPTY_DOCUMENT"):
        parse_document("resume.txt", "text/plain", b"", "RESUME", 100)
    with pytest.raises(ValueError, match="UNSUPPORTED_FILE_TYPE"):
        parse_document("resume.exe", "application/octet-stream", b"x", "RESUME", 100)


def test_structured_analysis_validates_score_and_evidence() -> None:
    resume = parse_document("resume.txt", "text/plain", b"Python project", "RESUME", 1000)
    jd = parse_document("jd.txt", "text/plain", b"Python and Kubernetes required", "JOB_DESCRIPTION", 1000)
    result = build_analysis(resume, jd, "mission-1")
    validate_analysis(result)
    assert result["match_analysis"]["overall_match_score"] == 50
    assert "kubernetes" in result["match_analysis"]["missing_skills"]
    assert result["limitations"]


def test_upload_endpoint_returns_structured_result(client) -> None:
    response = client.post(
        "/api/v1/missions/resume-jd/upload",
        files={"resume": ("resume.txt", b"Python experience", "text/plain"), "job_description": ("jd.txt", b"Python Kubernetes", "text/plain")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["result"]["match_analysis"]["overall_match_score"] == 50