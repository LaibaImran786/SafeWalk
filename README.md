# SafeWalk

AI-assisted personal journey safety prototype: React + FastAPI + SQLite + optional Gemma 4.
The UI uses a neumorphic (soft UI) design.

The core safety workflow (journey, check-ins, countdown, SOS, escalation) is controlled by the
backend and works with the AI service switched off.

## Run it

Backend (Python 3.10+):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Frontend (Node 18+), in a second terminal:

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxies /api to port 8000)
```

Tests: from the repo root run `pytest`.

Optional AI: copy `.env.example` to `.env` and point it at a Gemma runtime. Without it, the
briefing button returns standard tips and says AI is unavailable.

## Demo tips

Choose "Every 10 seconds (demo)" and a "10 seconds (demo)" warning. Let the ring run out to
see: missed check-in -> warning countdown -> simulated alert. Refresh the page mid-journey;
state is restored from SQLite. Deny location permission to see the app continue without coordinates.

## State machine

`ACTIVE -> ALERT_PENDING -> ALERT_TRIGGERED -> ENDED`
Check-in or cancel returns `ALERT_PENDING -> ACTIVE`. Manual SOS goes straight to `ALERT_TRIGGERED`.
The backend rejects early missed-check-ins, early or stale escalations, and anything after `ENDED`.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | /api/journeys | Create a journey |
| GET | /api/journeys/active | Load the open journey |
| POST | /api/journeys/{id}/location | Save GPS coordinates |
| POST | /api/journeys/{id}/checkin | Confirm safety, reset deadline |
| POST | /api/journeys/{id}/missed-checkin | Register a missed check-in |
| POST | /api/journeys/{id}/cancel-alert | Cancel a pending alert |
| POST | /api/journeys/{id}/sos | Manual SOS |
| POST | /api/journeys/{id}/escalate | Escalate an expired countdown |
| POST | /api/journeys/{id}/end | End the journey |
| GET | /api/journeys/{id}/alerts | List alerts |
| POST | /api/ai/briefing | Optional Gemma briefing / alert explanation |

## Limits

Notifications are **simulated**: nothing is sent to contacts or emergency services. No
background tracking, no authentication, single open journey at a time. Check the Gemma model
license before redistributing weights. Never commit real locations, contacts or secrets.
