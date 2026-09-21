"""Génère l'export CSV des abonnements, avec historique de changements.

Simule un export nocturne du système de facturation : une ligne par
changement d'état d'abonnement (souscription, upgrade, résiliation), pas un
état courant unique. C'est la matière première d'un dim_user en SCD Type 2.
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from generator.common import PLANS, User, weighted_choice

PLAN_WEIGHTS = [55, 25, 12, 8]  # free, monthly, yearly, business
UPGRADE_PROB_PER_DAY = 0.01
CANCEL_PROB_PER_DAY = 0.004


def _iso(d: date) -> str:
    return d.isoformat()


def build_subscription_history(rng: random.Random, users: list[User], start_date: date, days: int) -> list[dict]:
    rows: list[dict] = []
    end_date = start_date + timedelta(days=days - 1)

    for user in users:
        current_plan = weighted_choice(rng, PLANS, PLAN_WEIGHTS)
        started_at = user.signup_date
        status = "active"
        cancelled_at = None

        rows.append({
            "user_id": user.user_id,
            "plan": current_plan,
            "status": status,
            "started_at": _iso(started_at),
            "cancelled_at": "",
            "recorded_at": _iso(max(started_at, start_date)),
        })

        cursor = max(started_at, start_date)
        while cursor <= end_date and status == "active":
            cursor += timedelta(days=1)
            if current_plan != "free" and rng.random() < CANCEL_PROB_PER_DAY:
                status = "cancelled"
                cancelled_at = cursor
                rows.append({
                    "user_id": user.user_id,
                    "plan": current_plan,
                    "status": status,
                    "started_at": _iso(started_at),
                    "cancelled_at": _iso(cancelled_at),
                    "recorded_at": _iso(cursor),
                })
                break
            if current_plan == "free" and rng.random() < UPGRADE_PROB_PER_DAY:
                current_plan = weighted_choice(rng, PLANS[1:], PLAN_WEIGHTS[1:])
                started_at = cursor
                rows.append({
                    "user_id": user.user_id,
                    "plan": current_plan,
                    "status": "active",
                    "started_at": _iso(started_at),
                    "cancelled_at": "",
                    "recorded_at": _iso(cursor),
                })
    return rows


def write_subscriptions(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "plan", "status", "started_at", "cancelled_at", "recorded_at"])
        writer.writeheader()
        writer.writerows(rows)
