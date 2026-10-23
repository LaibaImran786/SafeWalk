from unittest.mock import patch

from conftest import PAYLOAD


def url(j, tail):
    return f"/api/journeys/{j['id']}/{tail}"


def test_create_journey_is_active(client, journey):
    assert journey["status"] == "ACTIVE"
    assert client.get("/api/journeys/active").json()["journey"]["id"] == journey["id"]


def test_validation_rejects_bad_input(client):
    assert client.post("/api/journeys", json={**PAYLOAD, "destination": "  "}).status_code == 422
    assert client.post("/api/journeys", json={**PAYLOAD, "warning_seconds": 1}).status_code == 422


def test_only_one_open_journey(client, journey):
    assert client.post("/api/journeys", json=PAYLOAD).status_code == 409


def test_location_denied_leaves_coordinates_null(client, journey):
    assert journey["latitude"] is None and journey["longitude"] is None
    bad = client.post(url(journey, "location"), json={"latitude": 999, "longitude": 0})
    assert bad.status_code == 422
    ok = client.post(url(journey, "location"), json={"latitude": 31.5, "longitude": 74.3})
    assert ok.json()["journey"]["latitude"] == 31.5


def test_successful_checkin_resets_deadline_without_alert(client, journey, clock):
    clock.advance(30)
    r = client.post(url(journey, "checkin")).json()["journey"]
    assert r["checkin_deadline"] > journey["checkin_deadline"]
    assert client.get(url(journey, "alerts")).json()["alerts"] == []


def test_missed_checkin_requires_deadline_and_sets_pending(client, journey, clock):
    assert client.post(url(journey, "missed-checkin")).status_code == 409  # too early
    clock.advance(61)
    r = client.post(url(journey, "missed-checkin")).json()
    assert r["journey"]["status"] == "ALERT_PENDING"
    assert r["alert"]["status"] == "pending"


def test_cancel_countdown_and_reject_stale_escalation(client, journey, clock):
    clock.advance(61)
    client.post(url(journey, "missed-checkin"))
    r = client.post(url(journey, "cancel-alert")).json()
    assert r["journey"]["status"] == "ACTIVE"
    assert r["alert"]["status"] == "cancelled"
    assert client.post(url(journey, "escalate")).status_code == 409


def test_escalation_waits_for_expiry_then_creates_one_simulated_alert(client, journey, clock):
    clock.advance(61)
    client.post(url(journey, "missed-checkin"))
    assert client.post(url(journey, "escalate")).status_code == 409  # countdown still running
    clock.advance(21)
    r = client.post(url(journey, "escalate")).json()
    assert r["journey"]["status"] == "ALERT_TRIGGERED"
    assert r["alert"]["status"] == "simulated"
    assert client.post(url(journey, "escalate")).status_code == 409  # no duplicates
    assert len(client.get(url(journey, "alerts")).json()["alerts"]) == 1


def test_manual_sos_is_immediate(client, journey):
    r = client.post(url(journey, "sos")).json()
    assert r["journey"]["status"] == "ALERT_TRIGGERED"
    assert r["alert"]["reason"] == "manual_sos"
    assert "SIMULATED" in r["alert"]["message"]


def test_sos_during_countdown_reuses_single_alert(client, journey, clock):
    clock.advance(61)
    client.post(url(journey, "missed-checkin"))
    client.post(url(journey, "sos"))
    assert len(client.get(url(journey, "alerts")).json()["alerts"]) == 1


def test_end_journey_blocks_further_escalation(client, journey):
    assert client.post(url(journey, "end")).json()["journey"]["status"] == "ENDED"
    for tail in ("sos", "escalate", "checkin", "missed-checkin", "end"):
        assert client.post(url(journey, tail)).status_code == 409
    assert client.get("/api/journeys/active").json()["journey"] is None


def test_gemma_unavailable_does_not_break_core(client, journey):
    with patch("gemma_service.httpx.post", side_effect=ConnectionError("down")):
        r = client.post("/api/ai/briefing", json={"traveler_name": "A", "destination": "B"})
    assert r.status_code == 200 and r.json()["ai_available"] is False
    assert client.post(url(journey, "sos")).json()["journey"]["status"] == "ALERT_TRIGGERED"
