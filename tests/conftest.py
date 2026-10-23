import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["SAFEWALK_DB_URL"] = f"sqlite:///{_tmp}/test.db"

from datetime import timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import safety_service  # noqa: E402
from app import app  # noqa: E402
from database import Base, engine  # noqa: E402


class Clock:
    def __init__(self):
        self.offset = timedelta(0)

    def advance(self, seconds):
        self.offset += timedelta(seconds=seconds)


@pytest.fixture()
def clock(monkeypatch):
    c = Clock()
    real_now = safety_service.now
    monkeypatch.setattr(safety_service, "now", lambda: real_now() + c.offset)
    return c


@pytest.fixture()
def client(clock):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return TestClient(app)


PAYLOAD = {
    "traveler_name": "Ayesha",
    "destination": "Lahore Fort",
    "trusted_contact": "Sara",
    "trusted_contact_phone": "+92 300 0000000",
    "checkin_interval_seconds": 60,
    "warning_seconds": 20,
}


@pytest.fixture()
def journey(client):
    r = client.post("/api/journeys", json=PAYLOAD)
    assert r.status_code == 201
    return r.json()["journey"]
