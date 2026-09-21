# Générateur de données KaraSing

Données 100% synthétiques (aucun vrai titre, artiste ou marque). Génération
reproductible via une graine (`--seed`).

## Usage

```bash
python -m generator --days 30 --seed 42
```

Options principales (voir `python -m generator --help` pour la liste complète) :

- `--days` : nombre de jours d'historique (défaut 30)
- `--start-date` : premier jour généré, `YYYY-MM-DD` (défaut `2026-01-01`)
- `--seed` : graine aléatoire
- `--out-dir` : dossier de sortie (défaut `data/raw`)
- `--n-users`, `--n-songs`, `--n-artists`, `--n-rights-holders` : volumétrie
- `--inject-anomaly {duplicate_events,late_arrival,null_keys,volume_spike,volume_drop}` :
  injecte une anomalie marquée sur un jour donné (voir `--anomaly-day`), en plus
  du bruit réaliste de fond toujours présent (petit taux de doublons/clés nulles).

## Sorties (`data/raw/`)

| Source | Format | Chemin |
|---|---|---|
| Événements applicatifs | JSONL, 1 fichier/jour | `app_events/YYYY-MM-DD.jsonl` |
| Catalogue (songs/artists/rights_holders) | CSV, snapshot quotidien | `catalogue/YYYY-MM-DD/*.csv` |
| Abonnements | CSV, historique de changements | `subscriptions/subscriptions_export.csv` |
| Bars (venues + réservations) | CSV | `bookings/venues.csv`, `bookings/bookings.csv` |

### `app_events` — types d'événements (discriminés par `event_type`)

- `song_played` : `event_id, event_type, user_id, song_id, session_id, device, country, played_at, duration_sec, completed`
- `song_searched` : `event_id, event_type, user_id, session_id, device, country, searched_at, query, results_count`
- `favorite_added` : `event_id, event_type, user_id, song_id, session_id, device, country, added_at`

Horodatages en UTC (`...Z`).

### Caractéristiques réalistes de la donnée brute (pas des bugs du générateur)

- ~4% des chansons n'ont pas d'`artist_id` (musique traditionnelle, domaine public).
- Petit taux de doublons et de clés nulles dans `app_events`, même sans `--inject-anomaly`.
- `bookings.csv` stocke `booked_at`/`slot_start` en **heure locale naïve** (sans
  offset), comme le ferait une caisse de bar — la conversion en UTC est à la
  charge du pipeline consommateur.

## Cas d'usage : exercice d'incident (jalon 6)

```bash
python -m generator --days 30 --inject-anomaly volume_drop --anomaly-day 25
```

Génère un run normal sauf sur le jour d'index 25 (0 = `--start-date`), où
l'anomalie choisie est appliquée avec une intensité largement supérieure au
bruit de fond.
