"""Génère les réservations des 3 bars karaoké.

Les horodatages sont volontairement stockés en heure locale "naïve" (sans
offset, comme le ferait la caisse/le logiciel de réservation d'un bar) :
c'est une caractéristique réaliste de la donnée brute, pas une anomalie. La
conversion en UTC est la responsabilité du pipeline qui la consomme — et
c'est justement ce que la version "prestataire" va mal faire (jalon 2).
"""
from __future__ import annotations

import csv
import random
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path

from generator.common import VENUES

OPEN_HOUR = 17
CLOSE_HOUR = 24  # minuit
SLOT_DURATION_MIN = 60


def _iso_local(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")  # pas de suffixe : heure locale naïve, comme la caisse du bar


def generate_bookings_for_day(rng: random.Random, day: date) -> list[dict]:
    rows = []
    for venue in VENUES:
        n_bookings = rng.randint(3, 10)
        for _ in range(n_bookings):
            room = rng.choice(venue["rooms"])
            slot_hour = rng.randint(OPEN_HOUR, CLOSE_HOUR - 1)
            slot_start = datetime.combine(day, time(hour=slot_hour % 24))
            booked_at = slot_start - timedelta(days=rng.randint(0, 14), hours=rng.randint(0, 12))
            rows.append({
                "booking_id": str(uuid.uuid4()),
                "venue_id": venue["venue_id"],
                "room_id": room,
                "booked_at": _iso_local(booked_at),
                "slot_start": _iso_local(slot_start),
                "party_size": rng.randint(2, 12),
                "amount_eur": round(rng.uniform(60, 240), 2),
            })
    return rows


def write_venues(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["venue_id", "name", "city", "timezone"])
        for v in VENUES:
            writer.writerow([v["venue_id"], v["name"], v["city"], v["timezone"]])


def write_bookings(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["booking_id", "venue_id", "room_id", "booked_at", "slot_start",
                                                 "party_size", "amount_eur"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)
