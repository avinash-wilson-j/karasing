"""Génère le catalogue (songs/artists/rights_holders) et ses snapshots CSV quotidiens.

Simule une "API catalogue" externe qui n'expose qu'un snapshot complet par jour
(pas de flux de changements) : quelques titres et ayants droit évoluent d'un
jour sur l'autre (nouveaux titres, fin de licence, changement de taux de
redevance), ce qui donne de la matière pour du SCD Type 2 côté SQLMesh.
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

from generator.common import (
    GENRES,
    LANGUAGE_WEIGHTS,
    LANGUAGES,
    Artist,
    RightsHolder,
    Song,
    weighted_choice,
)

# Part des titres sans artiste crédité (musique traditionnelle, domaine public,
# jingles internes...) : donnée réaliste, pas une anomalie injectée.
NO_ARTIST_RATE = 0.04

# Chaque jour, une petite fraction du catalogue évolue.
DAILY_NEW_SONGS_RATE = 0.01  # nouvelles chansons ajoutées / jour, proportion du catalogue initial
DAILY_LICENSE_CHANGE_RATE = 0.005
DAILY_ROYALTY_CHANGE_RATE = 0.002


def _make_artists(rng: random.Random, fake: Faker, n: int) -> list[Artist]:
    return [
        Artist(artist_id=f"art_{i:04d}", name=fake.name(), country=weighted_choice(
            rng, ["FR", "BE", "GB", "US", "ES", "DE", "IT"], [30, 15, 15, 20, 8, 7, 5]
        ))
        for i in range(1, n + 1)
    ]


def _make_rights_holders(rng: random.Random, fake: Faker, n: int) -> list[RightsHolder]:
    return [
        RightsHolder(
            rights_holder_id=f"rh_{i:03d}",
            name=fake.company() + " Music Rights",
            royalty_rate_eur=round(rng.uniform(0.002, 0.012), 5),
        )
        for i in range(1, n + 1)
    ]


def _make_song(rng: random.Random, fake: Faker, song_id: str, artists: list[Artist],
                rights_holders: list[RightsHolder], catalog_start: date) -> Song:
    has_artist = rng.random() > NO_ARTIST_RATE
    release_year = rng.randint(1975, catalog_start.year)
    license_days = rng.randint(180, 1500)
    return Song(
        song_id=song_id,
        title=fake.sentence(nb_words=rng.randint(2, 5)).rstrip("."),
        artist_id=rng.choice(artists).artist_id if has_artist else None,
        genre=weighted_choice(rng, GENRES, [14, 12, 12, 10, 10, 10, 8, 8, 10, 6]),
        language=weighted_choice(rng, LANGUAGES, LANGUAGE_WEIGHTS),
        release_year=release_year,
        licensed_until=catalog_start + timedelta(days=license_days),
        rights_holder_id=rng.choice(rights_holders).rights_holder_id if rng.random() > 0.02 else None,
    )


def build_catalogue(rng: random.Random, fake: Faker, n_songs: int, n_artists: int,
                     n_rights_holders: int, catalog_start: date):
    artists = _make_artists(rng, fake, n_artists)
    rights_holders = _make_rights_holders(rng, fake, n_rights_holders)
    songs = [
        _make_song(rng, fake, f"song_{i:05d}", artists, rights_holders, catalog_start)
        for i in range(1, n_songs + 1)
    ]
    return songs, artists, rights_holders


def mutate_catalogue(rng: random.Random, fake: Faker, songs: list[Song], artists: list[Artist],
                      rights_holders: list[RightsHolder], today: date, next_song_seq: list[int]) -> list[Song]:
    """Applique les évolutions du jour et renvoie les éventuelles nouvelles chansons."""
    new_songs = []
    for song in songs:
        if rng.random() < DAILY_LICENSE_CHANGE_RATE:
            song.licensed_until = today + timedelta(days=rng.randint(30, 900))
        if rng.random() < DAILY_ROYALTY_CHANGE_RATE and rights_holders:
            song.rights_holder_id = rng.choice(rights_holders).rights_holder_id

    n_new = int(len(songs) * DAILY_NEW_SONGS_RATE * rng.uniform(0.5, 1.5))
    for _ in range(n_new):
        song_id = f"song_{next_song_seq[0]:05d}"
        next_song_seq[0] += 1
        new_songs.append(_make_song(rng, fake, song_id, artists, rights_holders, today))
    songs.extend(new_songs)
    return songs


def write_snapshot(day_dir: Path, songs: list[Song], artists: list[Artist], rights_holders: list[RightsHolder]) -> None:
    day_dir.mkdir(parents=True, exist_ok=True)

    with (day_dir / "songs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["song_id", "title", "artist_id", "genre", "language", "release_year",
                          "licensed_until", "rights_holder_id"])
        for s in songs:
            writer.writerow([s.song_id, s.title, s.artist_id or "", s.genre, s.language,
                              s.release_year, s.licensed_until.isoformat(), s.rights_holder_id or ""])

    with (day_dir / "artists.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["artist_id", "name", "country"])
        for a in artists:
            writer.writerow([a.artist_id, a.name, a.country])

    with (day_dir / "rights_holders.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rights_holder_id", "name", "royalty_rate_eur"])
        for rh in rights_holders:
            writer.writerow([rh.rights_holder_id, rh.name, rh.royalty_rate_eur])
