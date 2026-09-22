"""Point d'entrée du générateur de données KaraSing.

Usage :
    python -m generator --days 30 --seed 42
    python -m generator --days 30 --inject-anomaly volume_drop --anomaly-day 25
"""
from __future__ import annotations

import argparse
import random
import shutil
from datetime import date
from pathlib import Path

from generator import bookings, catalogue, events, subscriptions
from generator.common import build_users, daterange, make_faker
from generator.events import ANOMALY_TYPES


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère les données synthétiques KaraSing.")
    p.add_argument("--days", type=int, default=30, help="Nombre de jours d'historique à générer.")
    p.add_argument("--start-date", type=str, default="2026-01-01", help="Premier jour généré (YYYY-MM-DD).")
    p.add_argument("--seed", type=int, default=42, help="Graine aléatoire, pour reproductibilité.")
    p.add_argument("--out-dir", type=str, default="data/raw", help="Dossier de sortie.")

    p.add_argument("--n-users", type=int, default=600)
    p.add_argument("--n-songs", type=int, default=900)
    p.add_argument("--n-artists", type=int, default=200)
    p.add_argument("--n-rights-holders", type=int, default=45)

    p.add_argument("--inject-anomaly", choices=ANOMALY_TYPES, default=None,
                    help="Injecte une anomalie plus marquée sur --anomaly-day (par défaut : le dernier jour généré).")
    p.add_argument("--anomaly-day", type=int, default=None,
                    help="Index du jour (0 = --start-date) où injecter l'anomalie.")
    p.add_argument("--late-arrival-days", type=int, default=3,
                    help="Décalage (en jours) appliqué au fichier de sortie pour l'anomalie 'late_arrival'.")
    p.add_argument("--v2-from-day", type=int, default=None,
                    help="Index du jour (0 = --start-date) a partir duquel le backend simule son renommage "
                         "duration_sec -> duration_ms sur les evenements song_played.")
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    start_date = date.fromisoformat(args.start_date)
    anomaly_day = args.anomaly_day if args.anomaly_day is not None else args.days - 1
    out_dir = Path(args.out_dir)

    rng = random.Random(args.seed)
    fake = make_faker(args.seed)

    if out_dir.exists():
        shutil.rmtree(out_dir)  # chaque run repart de zero : pas de cumul entre deux executions

    print(f"[generator] seed={args.seed} days={args.days} start={start_date}")

    users = build_users(rng, fake, args.n_users, start_date)
    songs, artists, rights_holders = catalogue.build_catalogue(
        rng, fake, args.n_songs, args.n_artists, args.n_rights_holders, start_date
    )
    next_song_seq = [args.n_songs + 1]

    bookings.write_venues(out_dir / "bookings" / "venues.csv")
    all_subscription_rows = subscriptions.build_subscription_history(rng, users, start_date, args.days)
    subscriptions.write_subscriptions(out_dir / "subscriptions" / "subscriptions_export.csv", all_subscription_rows)

    for i, day in enumerate(daterange(start_date, args.days)):
        songs = catalogue.mutate_catalogue(rng, fake, songs, artists, rights_holders, day, next_song_seq)
        catalogue.write_snapshot(out_dir / "catalogue" / day.isoformat(), songs, artists, rights_holders)

        day_events = events.generate_events_for_day(rng, fake, users, songs, day)
        if args.v2_from_day is not None and i >= args.v2_from_day:
            day_events = events.apply_schema_v2(day_events)
        late_arrival_days = 0
        if args.inject_anomaly and i == anomaly_day:
            print(f"[generator] anomalie '{args.inject_anomaly}' injectée sur {day}")
            if args.inject_anomaly == "late_arrival":
                late_arrival_days = args.late_arrival_days
            else:
                day_events = events.apply_anomaly(rng, day_events, args.inject_anomaly)
        events.write_day(out_dir / "app_events", day, day_events, late_arrival_days=late_arrival_days)

        day_bookings = bookings.generate_bookings_for_day(rng, day)
        bookings.write_bookings(out_dir / "bookings" / "bookings.csv", day_bookings)

    print(f"[generator] terminé. Sorties dans {out_dir.resolve()}")


if __name__ == "__main__":
    main()
