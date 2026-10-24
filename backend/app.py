"""SafeWalk FastAPI application: REST API, validation and orchestration."""
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
import os

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured")
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import gemma_service  # noqa: E402
import safety_service as safety  # noqa: E402
from database import Alert, Journey, get_db, init_db  # noqa: E402
from schemas import BriefingIn, JourneyCreate, LocationIn  # noqa: E402


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="SafeWalk API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173","https://safewalk-iota.vercel.app"],
        allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(safety.SafetyError)
async def safety_error_handler(_, exc: safety.SafetyError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat() + "Z" if dt else None

 
def journey_out(j: Journey) -> dict:
    return {
        "id": j.id,
        "traveler_name": j.traveler_name,
        "destination": j.destination,
        "trusted_contact": j.trusted_contact,
        "trusted_contact_phone": j.trusted_contact_phone,
        "status": j.status,
        "latitude": j.latitude,
        "longitude": j.longitude,
        "location_updated_at": iso(j.location_updated_at),
        "checkin_interval_seconds": j.checkin_interval_seconds,
        "warning_seconds": j.warning_seconds,
        "checkin_deadline": iso(j.checkin_deadline),
        "warning_deadline": iso(j.warning_deadline),
        "created_at": iso(j.created_at),
        "ended_at": iso(j.ended_at),
        "server_time": iso(safety.now()),
    }


def alert_out(a: Alert | None) -> dict | None:
    if a is None:
        return None
    return {
        "id": a.id,
        "journey_id": a.journey_id,
        "reason": a.reason,
        "status": a.status,
        "message": a.message,
        "latitude": a.latitude,
        "longitude": a.longitude,
        "location_updated_at": iso(a.location_updated_at),
        "created_at": iso(a.created_at),
    }


def result(journey: Journey, alert: Alert | None = None) -> dict:
    return {"journey": journey_out(journey), "alert": alert_out(alert)}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/journeys", status_code=201)
def create_journey(body: JourneyCreate, db: Session = Depends(get_db)):
    return result(safety.create_journey(db, body.model_dump()))


@app.get("/api/journeys/active")
def active_journey(db: Session = Depends(get_db)):
    journey = safety.get_active(db)
    return {"journey": journey_out(journey) if journey else None}


@app.post("/api/journeys/{journey_id}/location")
def save_location(journey_id: int, body: LocationIn, db: Session = Depends(get_db)):
    return result(safety.add_location(db, journey_id, body.latitude, body.longitude))


@app.post("/api/journeys/{journey_id}/checkin")
def checkin(journey_id: int, db: Session = Depends(get_db)):
    return result(safety.checkin(db, journey_id))


@app.post("/api/journeys/{journey_id}/missed-checkin")
def missed_checkin(journey_id: int, db: Session = Depends(get_db)):
    return result(*safety.missed_checkin(db, journey_id))


@app.post("/api/journeys/{journey_id}/cancel-alert")
def cancel_alert(journey_id: int, db: Session = Depends(get_db)):
    return result(*safety.cancel_alert(db, journey_id))


@app.post("/api/journeys/{journey_id}/sos")
def sos(journey_id: int, db: Session = Depends(get_db)):
    return result(*safety.trigger_sos(db, journey_id))


@app.post("/api/journeys/{journey_id}/escalate")
def escalate(journey_id: int, db: Session = Depends(get_db)):
    return result(*safety.escalate(db, journey_id))


@app.post("/api/journeys/{journey_id}/end")
def end(journey_id: int, db: Session = Depends(get_db)):
    return result(safety.end_journey(db, journey_id))


@app.get("/api/journeys/{journey_id}/alerts")
def alerts(journey_id: int, db: Session = Depends(get_db)):
    return {"alerts": [alert_out(a) for a in safety.list_alerts(db, journey_id)]}


@app.post("/api/ai/briefing")
def ai_briefing(body: BriefingIn):
    # Sync endpoint: FastAPI runs it in a worker thread, so a slow model never blocks safety calls.
    return gemma_service.generate_text(
        body.kind, body.traveler_name, body.destination,
        body.checkin_interval_seconds, body.reason,
    )
