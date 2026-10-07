from scayl import service
from scayl.contracts import ReviewState


def test_service_client_loads_fixture_and_reviews_in_isolated_storage(monkeypatch, tmp_path):
    from app import service_client

    service.reload()
    monkeypatch.setattr(service, "bundle_path", lambda: service.FIXTURE)
    monkeypatch.setenv("SCAYL_STATE_DIR", str(tmp_path))
    try:
        bundle = service_client.load_bundle()
        assert bundle.snapshot_version == "fixture-synthetic-0"
        event = service_client.get_event("EVT-0001")
        record = service_client.review(event.event_id, ReviewState.EN_REVISION, "editor", "Verificar daños")
        assert record.event_id == event.event_id
        assert service_client.current_state(event.event_id) == ReviewState.EN_REVISION
        assert service_client.review_history(event.event_id) == [record]
    finally:
        service.reload()
