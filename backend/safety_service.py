"""Core safety state machine. Deliberately has NO dependency on the AI service.

States: ACTIVE -> ALERT_PENDING -> ALERT_TRIGGERED -> ENDED
        ACTIVE -> ALERT_TRIGGERED (manual SOS)
        ALERT_PENDING -> ACTIVE (check-in / cancel)
        any non-ended state -> ENDED
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Alert, Journey

ACTIVE = "ACTIVE"
ALERT_PENDING = "ALERT_PENDING"
ALERT_TRIGGERED = "ALERT_TRIGGERED"
ENDED = "ENDED"

# Small tolerance so a browser clock a fraction of a second early is not rejected.
GRACE = timedelta(seconds=1)


class SafetyError(Exception):
    def __init__(self, message: str, status_code: int = 409):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def now() -> datetime:
    """Naive UTC 'now'. Tests monkeypatch this function to move time."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _get(session: Session, journey_id: int) -> Journey:
    journey = session.get(Journey, journey_id)
    if journey is None:
        raise SafetyError("Journey not found.", 404)
    return journey


def _pending_alert(session: Session, journey_id: int) -> Alert | None:
    return session.scalars(
        select(Alert).where(Alert.journey_id == journey_id, Alert.status == "pending")
    ).first()


def _require(journey: Journey, allowed: tuple[str, ...], action: str) -> None:
    if journey.status not in allowed:
        raise SafetyError(
            f"Cannot {action}: journey is {journey.status}, expected {' or '.join(allowed)}."
        )


def _reset_deadline(journey: Journey) -> None:
    journey.checkin_deadline = now() + timedelta(seconds=journey.checkin_interval_seconds)
    journey.warning_deadline = None


def create_journey(session: Session, data: dict) -> Journey:
    open_journey = session.scalars(select(Journey).where(Journey.status != ENDED)).first()
    if open_journey is not None:
        raise SafetyError("A journey is already in progress. End it before starting a new one.")
    t = now()
    journey = Journey(
        **data,
        status=ACTIVE,
        created_at=t,
        checkin_deadline=t + timedelta(seconds=data["checkin_interval_seconds"]),
    )
    session.add(journey)
    session.commit()
    return journey


def get_active(session: Session) -> Journey | None:
    return session.scalars(
        select(Journey).where(Journey.status != ENDED).order_by(Journey.id.desc())
    ).first()


def add_location(session: Session, journey_id: int, lat: float, lon: float) -> Journey:
    journey = _get(session, journey_id)
    if journey.status == ENDED:
        raise SafetyError("Journey has ended; location is no longer recorded.")
    journey.latitude, journey.longitude, journey.location_updated_at = lat, lon, now()
    session.commit()
    return journey


def checkin(session: Session, journey_id: int) -> Journey:
    journey = _get(session, journey_id)
    _require(journey, (ACTIVE, ALERT_PENDING), "check in")
    pending = _pending_alert(session, journey_id)
    if pending:
        pending.status = "cancelled"
        pending.message += " Cancelled: traveler confirmed safety."
    journey.status = ACTIVE
    _reset_deadline(journey)
    session.commit()
    return journey


def missed_checkin(session: Session, journey_id: int) -> tuple[Journey, Alert]:
    journey = _get(session, journey_id)
    _require(journey, (ACTIVE,), "register a missed check-in")
    if now() + GRACE < journey.checkin_deadline:
        raise SafetyError("Check-in deadline has not passed yet.")
    t = now()
    journey.status = ALERT_PENDING
    journey.warning_deadline = t + timedelta(seconds=journey.warning_seconds)
    alert = Alert(
        journey_id=journey.id,
        reason="missed_checkin",
        status="pending",
        message=f"{journey.traveler_name} missed a check-in on the way to {journey.destination}.",
        latitude=journey.latitude,
        longitude=journey.longitude,
        location_updated_at=journey.location_updated_at,
        created_at=t,
    )
    session.add(alert)
    session.commit()
    return journey, alert


def cancel_alert(session: Session, journey_id: int) -> tuple[Journey, Alert | None]:
    journey = _get(session, journey_id)
    _require(journey, (ALERT_PENDING,), "cancel the warning")
    alert = _pending_alert(session, journey_id)
    if alert:
        alert.status = "cancelled"
        alert.message += " Cancelled by traveler before the countdown expired."
    journey.status = ACTIVE
    _reset_deadline(journey)
    session.commit()
    return journey, alert


def _finalize_alert(session: Session, journey: Journey, reason: str) -> Alert:
    """Shared by manual SOS and automatic escalation. Reuses the pending alert so
    exactly one record exists per incident."""
    t = now()
    alert = _pending_alert(session, journey.id)
    if alert is None:
        alert = Alert(journey_id=journey.id, created_at=t, message="")
        session.add(alert)
    alert.reason = reason
    alert.status = "simulated"  # no real SMS/WhatsApp provider is connected
    what = "Manual SOS pressed" if reason == "manual_sos" else "Check-in missed and warning expired"
    alert.message = (
        f"{what} by {journey.traveler_name} (destination: {journey.destination}). "
        f"SIMULATED notification to {journey.trusted_contact}; no real message was sent."
    )
    alert.latitude, alert.longitude = journey.latitude, journey.longitude
    alert.location_updated_at = journey.location_updated_at
    journey.status = ALERT_TRIGGERED
    journey.warning_deadline = None
    session.commit()
    return alert


def trigger_sos(session: Session, journey_id: int) -> tuple[Journey, Alert]:
    journey = _get(session, journey_id)
    _require(journey, (ACTIVE, ALERT_PENDING), "trigger SOS")
    return journey, _finalize_alert(session, journey, "manual_sos")


def escalate(session: Session, journey_id: int) -> tuple[Journey, Alert]:
    journey = _get(session, journey_id)
    if journey.status != ALERT_PENDING:
        raise SafetyError(f"Stale escalation rejected: journey is {journey.status}.")
    if now() + GRACE < journey.warning_deadline:
        raise SafetyError("Warning countdown has not expired yet.")
    return journey, _finalize_alert(session, journey, "missed_checkin")


def end_journey(session: Session, journey_id: int) -> Journey:
    journey = _get(session, journey_id)
    if journey.status == ENDED:
        raise SafetyError("Journey has already ended.")
    pending = _pending_alert(session, journey_id)
    if pending:
        pending.status = "cancelled"
        pending.message += " Cancelled: journey ended."
    journey.status = ENDED
    journey.ended_at = now()
    journey.warning_deadline = None
    session.commit()
    return journey


def list_alerts(session: Session, journey_id: int) -> list[Alert]:
    _get(session, journey_id)
    return list(
        session.scalars(select(Alert).where(Alert.journey_id == journey_id).order_by(Alert.id))
    )
