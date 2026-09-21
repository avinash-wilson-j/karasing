"""Constantes et fabriques d'entités partagées par les générateurs de sources."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta

from faker import Faker

COUNTRIES = ["FR", "BE", "DE", "ES", "IT", "GB", "CA", "US", "CH", "NL"]
# Le public est majoritairement francophone (FR/BE), avec une longue traîne internationale.
COUNTRY_WEIGHTS = [38, 22, 6, 6, 5, 5, 4, 4, 5, 5]

DEVICES = ["ios", "android", "web", "smart_tv"]
DEVICE_WEIGHTS = [35, 30, 25, 10]

GENRES = ["pop", "rock", "rap", "variete", "electro", "rnb", "reggae", "latino", "kids", "classique"]
LANGUAGES = ["fr", "en", "es", "de", "it", "nl"]
LANGUAGE_WEIGHTS = [45, 35, 6, 5, 5, 4]

PLANS = ["free", "monthly", "yearly", "business"]

# Les 3 bars exploités. Même fuseau horaire (Europe/Paris) pour tous : le bug
# classique "UTC vs local mal géré" n'a pas besoin de fuseaux différents,
# juste d'un oubli de conversion sur une donnée stockée en heure locale.
VENUES = [
    {"venue_id": "venue_lille", "name": "KaraSing Lille", "city": "Lille", "timezone": "Europe/Paris",
     "rooms": ["room_lille_1", "room_lille_2", "room_lille_3"]},
    {"venue_id": "venue_paris", "name": "KaraSing Paris", "city": "Paris", "timezone": "Europe/Paris",
     "rooms": ["room_paris_1", "room_paris_2", "room_paris_3", "room_paris_4"]},
    {"venue_id": "venue_bruxelles", "name": "KaraSing Bruxelles", "city": "Bruxelles", "timezone": "Europe/Paris",
     "rooms": ["room_bxl_1", "room_bxl_2"]},
]


def make_faker(seed: int) -> Faker:
    fake = Faker()
    Faker.seed(seed)
    return fake


@dataclass
class User:
    user_id: str
    country: str
    device: str
    signup_date: date


@dataclass
class Song:
    song_id: str
    title: str
    artist_id: str | None
    genre: str
    language: str
    release_year: int
    licensed_until: date
    rights_holder_id: str | None


@dataclass
class Artist:
    artist_id: str
    name: str
    country: str


@dataclass
class RightsHolder:
    rights_holder_id: str
    name: str
    royalty_rate_eur: float  # taux de redevance par écoute, en euros


def weighted_choice(rng: random.Random, options: list, weights: list):
    return rng.choices(options, weights=weights, k=1)[0]


def daterange(start: date, days: int):
    for i in range(days):
        yield start + timedelta(days=i)


def build_users(rng: random.Random, fake: Faker, n_users: int, start_date: date) -> list[User]:
    users = []
    for i in range(1, n_users + 1):
        signup_offset = rng.randint(0, 365)
        users.append(
            User(
                user_id=f"usr_{i:05d}",
                country=weighted_choice(rng, COUNTRIES, COUNTRY_WEIGHTS),
                device=weighted_choice(rng, DEVICES, DEVICE_WEIGHTS),
                signup_date=start_date - timedelta(days=signup_offset),
            )
        )
    return users
