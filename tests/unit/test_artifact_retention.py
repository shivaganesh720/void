from app.services.artifacts import ArtifactRetentionService


def test_artifact_registry_stores_and_retrieves_records() -> None:
    service = ArtifactRetentionService(path=":memory:")
    record = service.register_artifact(
        project_id="project-1",
        mission_id="mission-1",
        artifact_type="resume_jd_report",
        content="artifact-content",
        owner_id="user-1",
    )

    artifact = service.get_artifact(record["id"])
    assert artifact is not None
    assert artifact["content_hash"]
    assert artifact["status"] == "CREATED"


def test_artifact_retention_flags_expired_artifacts() -> None:
    service = ArtifactRetentionService(path=":memory:")
    expired = service.register_artifact(
        project_id="project-1",
        mission_id="mission-1",
        artifact_type="demo",
        content="old",
        owner_id="user-1",
        age_days=45,
    )

    assert service.should_expire(expired["id"]) is True
    assert service.list_expired() != []
