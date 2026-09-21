"""Génère les événements applicatifs (song_played, song_searched, favorite_added)
en JSONL, un fichier par jour, avec un peu de bruit réaliste par défaut et des
anomalies plus fortes injectables à la demande sur un jour donné.
"""
from __future__ import annotations

import json
import random
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path

from faker import Faker

from generator.common import Song, User

# --- Bruit réaliste toujours présent (retries client, etc.) ---
BASELINE_DUPLICATE_RATE = 0.003
BASELINE_NULL_KEY_RATE = 0.001

ANOMALY_TYPES = ["duplicate_events", "late_arrival", "null_keys", "volume_spike", "volume_drop"]


def _active_users_for_day(rng: random.Random, users: list[User], today: date) -> list[User]:
    eligible = [u for u in users if u.signup_date <= today]
    if not eligible:
        return []
    share = rng.uniform(0.12, 0.28)
    n_active = max(1, int(len(eligible) * share))
    return rng.sample(eligible, min(n_active, len(eligible)))


def _random_time_on(rng: random.Random, day: date) -> datetime:
    seconds = rng.randint(0, 24 * 3600 - 1)
    return datetime.combine(day, time()) + timedelta(seconds=seconds)


def _iso_utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _gen_session_events(rng: random.Random, fake: Faker, user: User, songs: list[Song], day: date) -> list[dict]:
    session_id = str(uuid.uuid4())
    events = []
    n_searches = rng.randint(0, 3)
    for _ in range(n_searches):
        events.append({
            "event_id": str(uuid.uuid4()),
            "event_type": "song_searched",
            "user_id": user.user_id,
            "session_id": session_id,
            "device": user.device,
            "country": user.country,
            "searched_at": _iso_utc(_random_time_on(rng, day)),
            "query": fake.word(),
            "results_count": rng.randint(0, 20),
        })

    n_plays = rng.randint(1, 6)
    played_songs = rng.sample(songs, min(n_plays, len(songs)))
    for song in played_songs:
        duration_sec = rng.randint(90, 280)
        completed = rng.random() < 0.7
        events.append({
            "event_id": str(uuid.uuid4()),
            "event_type": "song_played",
            "user_id": user.user_id,
            "song_id": song.song_id,
            "session_id": session_id,
            "device": user.device,
            "country": user.country,
            "played_at": _iso_utc(_random_time_on(rng, day)),
            "duration_sec": duration_sec if completed else rng.randint(5, duration_sec),
            "completed": completed,
        })
        if rng.random() < 0.08:
            events.append({
                "event_id": str(uuid.uuid4()),
                "event_type": "favorite_added",
                "user_id": user.user_id,
                "song_id": song.song_id,
                "session_id": session_id,
                "device": user.device,
                "country": user.country,
                "added_at": _iso_utc(_random_time_on(rng, day)),
            })
    return events


def _apply_baseline_noise(rng: random.Random, events: list[dict]) -> list[dict]:
    noisy = list(events)
    for ev in events:
        if rng.random() < BASELINE_DUPLICATE_RATE:
            noisy.append(dict(ev))
    for ev in noisy:
        if rng.random() < BASELINE_NULL_KEY_RATE:
            ev["user_id"] = None
    return noisy


def apply_anomaly(rng: random.Random, events: list[dict], anomaly: str) -> list[dict]:
    if anomaly == "duplicate_events":
        extra = rng.sample(events, k=max(1, int(len(events) * 0.35)))
        return events + [dict(e) for e in extra]
    if anomaly == "null_keys":
        for ev in events:
            if rng.random() < 0.15:
                key = "song_id" if ev["event_type"] != "song_searched" else "user_id"
                ev[key] = None
        return events
    if anomaly == "volume_spike":
        extra = [dict(e, event_id=str(uuid.uuid4())) for e in rng.choices(events, k=int(len(events) * 2.5))]
        return events + extra
    if anomaly == "volume_drop":
        keep = max(1, int(len(events) * 0.1))
        return rng.sample(events, keep)
    # "late_arrival" est géré au niveau de l'écriture (décalage du fichier de sortie).
    return events


def generate_events_for_day(rng: random.Random, fake: Faker, users: list[User], songs: list[Song],
                             day: date) -> list[dict]:
    events: list[dict] = []
    for user in _active_users_for_day(rng, users, day):
        events.extend(_gen_session_events(rng, fake, user, songs, day))
    return _apply_baseline_noise(rng, events)


def write_day(out_dir: Path, day: date, events: list[dict], late_arrival_days: int = 0) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target_day = day + timedelta(days=late_arrival_days)
    path = out_dir / f"{target_day.isoformat()}.jsonl"
    mode = "a" if path.exists() else "w"
    with path.open(mode, encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return path
