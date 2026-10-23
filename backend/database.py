"""SQLite + SQLAlchemy models for SafeWalk."""
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DEFAULT_DB = f"sqlite:///{Path(__file__).parent / 'safewalk.db'}"
DATABASE_URL = os.getenv("SAFEWALK_DB_URL", DEFAULT_DB)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Journey(Base):
    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    traveler_name: Mapped[str] = mapped_column(String(120))
    destination: Mapped[str] = mapped_column(String(200))
    trusted_contact: Mapped[str] = mapped_column(String(120))
    trusted_contact_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    checkin_interval_seconds: Mapped[int] = mapped_column(Integer)
    warning_seconds: Mapped[int] = mapped_column(Integer)
    checkin_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    warning_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journey_id: Mapped[int] = mapped_column(ForeignKey("journeys.id"), index=True)
    reason: Mapped[str] = mapped_column(String(30))  # manual_sos | missed_checkin
    status: Mapped[str] = mapped_column(String(20))  # pending | simulated | cancelled | failed
    message: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
