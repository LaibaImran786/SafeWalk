from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, StringConstraints

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Place = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, max_length=40)]


class JourneyCreate(BaseModel):
    traveler_name: Name
    destination: Place
    trusted_contact: Name
    trusted_contact_phone: Optional[Phone] = None
    checkin_interval_seconds: int = Field(ge=10, le=86400)
    warning_seconds: int = Field(ge=5, le=600)


class LocationIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class BriefingIn(BaseModel):
    kind: Literal["briefing", "alert_explanation"] = "briefing"
    traveler_name: Name
    destination: Place
    checkin_interval_seconds: Optional[int] = Field(default=None, ge=1, le=86400)
    reason: Optional[Annotated[str, StringConstraints(max_length=40)]] = None
