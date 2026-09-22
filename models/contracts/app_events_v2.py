"""Contrat de donnees versionne pour les evenements song_played (v2).

v2 absorbe le renommage backend duration_sec -> duration_ms (en millisecondes)
tout en restant compatible avec les evenements v1 encore en circulation.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ValidationError, model_validator


class SongPlayedEventV2(BaseModel):
    event_id: str
    event_type: str
    user_id: str
    song_id: str
    session_id: str
    device: str
    country: str
    played_at: datetime
    duration_sec: int = Field(ge=0)
    completed: bool

    @model_validator(mode="before")
    @classmethod
    def normalize_duration(cls, data: dict) -> dict:
        # Si duration_sec est absent mais duration_ms present, on convertit.
        if data.get("duration_sec") is None and data.get("duration_ms") is not None: 
            data = {**data, "duration_sec": data.get("duration_ms")/1000}
        return data


def validate_song_played_v2(row: dict) -> tuple[bool, str | None]:
    try:
        SongPlayedEventV2(**row)
        return True, None
    except ValidationError as e:
        return False, str(e)