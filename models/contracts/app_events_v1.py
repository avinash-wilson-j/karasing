"""Contrat de donnees versionne pour les evenements song_played (v1)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ValidationError


class SongPlayedEventV1(BaseModel):
    event_id: str
    event_type: str
    user_id: str
    song_id: str
    session_id: str
    device: str
    country: str
    played_at: datetime
    duration_sec: int = Field(ge=0)  # contrainte : jamais negatif
    completed: bool


def validate_song_played(row: dict) -> tuple[bool, str | None]:
    """Valide une ligne brute contre le contrat v1. Retourne (est_valide, message_erreur)."""
    try:
        song_played = SongPlayedEventV1(**row)
        return True, None
    except ValidationError as e:
        return False, f'Err {e}'