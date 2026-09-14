import pytest

from app.utils.files import FileMetadata, validate_upload
from app.capabilities.resume_jd.service import analyze_resume_against_jd


def test_unsafe_upload_is_rejected() -> None:
    with pytest.raises(ValueError, match="INVALID_FILE"):
        validate_upload(FileMetadata("..\\secret.txt", "text/plain", 10), 100)
    with pytest.raises(ValueError, match="EMPTY_DOCUMENT"):
        validate_upload(FileMetadata("empty.txt", "text/plain", 0), 100)
    with pytest.raises(ValueError, match="FILE_TOO_LARGE"):
        validate_upload(FileMetadata("big.pdf", "application/pdf", 101), 100)
    with pytest.raises(ValueError, match="UNSUPPORTED_FILE_TYPE"):
        validate_upload(FileMetadata("test.jpg", "image/jpeg", 10), 100)
    with pytest.raises(ValueError, match="INVALID_FILE"):
        validate_upload(FileMetadata("script.txt", "application/x-sh", 10), 100)


def test_resume_analysis_marks_missing_skills_without_fabricating_them() -> None:
    result = analyze_resume_against_jd("Python and SQL experience", "Python, SQL, and Kubernetes required")
    assert "python" in result.matching_skills
    assert "kubernetes" in result.missing_skills
    assert all("kubernetes" not in evidence.quote for evidence in result.evidence if evidence.source == "resume")
    assert result.recommendations