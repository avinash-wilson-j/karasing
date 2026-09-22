# Jalon 3 — Récap : SQLMesh init, contrats, quarantaine

## Ce qui a été construit

**Couche `raw/`** (exposition brute, un modèle par source) :
- `raw.raw_bookings` (`VIEW`) — CSV unique, aucune transformation.
- `raw.raw_catalogue_songs` (`INCREMENTAL_BY_TIME_RANGE`, `batch_size 1`) — un snapshot CSV par jour, chemin du fichier construit avec `@start_ds`.
- `raw.raw_subscriptions` (`VIEW`) — CSV unique avec historique de changements.
- `raw.raw_app_events` (`FULL`) — glob de tous les `.jsonl`, `event_date` dérivé du contenu (`played_at`/`searched_at`/`added_at`), pas du nom de fichier.

**Couche `staging/`** :
- `staging.stg_bookings` — corrige la conversion UTC/local (`AT TIME ZONE 'Europe/Paris' AT TIME ZONE 'UTC'`), testée par un test unitaire SQLMesh sur un cas d'été (CEST).
- `staging.stg_catalogue_songs` — passage propre depuis le raw, incrémental.
- `staging.stg_subscriptions` — typage des dates, gestion des abonnements actifs (`cancelled_at IS NULL`).
- `staging.stg_song_played` / `staging.app_events_quarantine` — modèles **Python**, contrat de données Pydantic (voir ci-dessous).

**Contrat de données versionné** (`models/contracts/`, logique partagée dans `app_events_v1.py` / `app_events_v2.py`) :
- v1 : `song_played` valide = tous les champs obligatoires présents et typés (`duration_sec >= 0`, etc.).
- v2 : absorbe le renommage backend `duration_sec → duration_ms` via un `model_validator(mode="before")` qui normalise la donnée brute avant validation — les consommateurs en aval ne voient jamais `duration_ms`.
- Les lignes qui échouent la validation partent dans `staging.app_events_quarantine` avec le message d'erreur, au lieu de casser silencieusement le pipeline.

## Concepts SQLMesh démontrés

| Concept | Où |
|---|---|
| `kind VIEW` / `FULL` / `INCREMENTAL_BY_TIME_RANGE` | bookings (VIEW/FULL), catalogue (incrémental) |
| Macros de date `@start_ds`/`@end_ds`, `batch_size` | `raw_catalogue_songs` |
| Modèles Python (`@model`, `ExecutionContext`, `context.resolve_table`) | contrat `app_events` |
| Environnements virtuels `dev` vs `prod` | tout le jalon (debug en `dev` avant promotion) |
| `sqlmesh plan` vs `sqlmesh plan --restate-model` | voir "Piège" ci-dessous |
| Test unitaire SQLMesh (`tests/*.yaml`) | `test_stg_bookings.yaml` (cas DST) |
| Breaking vs non-breaking change | affiché automatiquement par `sqlmesh plan` à chaque modif de modèle |

## Le piège à retenir : `plan` vs `--restate-model`

- `sqlmesh plan` : relit les fichiers, **détecte un changement de code**, et propose le backfill nécessaire.
- `sqlmesh plan --restate-model X` : force le **retraitement de données déjà calculées** avec la version de modèle **déjà enregistrée** — ne relit pas le code s'il a changé sans passer par un `plan` classique.

On s'est fait avoir en pensant que `--restate-model` suffisait après avoir modifié le contrat Python : il retraitait avec l'ancien contrat (toujours en quarantaine à 2297 lignes) jusqu'à ce qu'on relance un `plan` classique.

## Le breaking change, bout en bout

1. Simulation : le générateur (`--v2-from-day N`) fait basculer le backend en format v2 sur les derniers jours.
2. Avec le contrat v1 seul : la quarantaine explose (22 → 2297 lignes, ~17,8% du volume) — le contrat **détecte** le problème au lieu de le laisser passer.
3. Contrat v2 (avec normalisation `duration_ms → duration_sec`) : quarantaine revenue à la normale (11 lignes, bruit de fond habituel).

## Comparaison chiffrée legacy vs SQLMesh

| Métrique | `legacy/` | SQLMesh | Écart |
|---|---|---|---|
| Écoutes comptées (total) | 12 349 | 12 888 | +539 (chansons sans artiste, perdues par le `INNER JOIN` legacy) |
| Utilisateurs actifs (05/01/2026) | 9 | 129 | ×14 (`_client_seq` vs `user_id`) |

## Bug annexe corrigé au passage (pas SQLMesh, le générateur)

`generator/cli.py` écrivait les fichiers en mode "append" à chaque exécution au lieu de repartir de zéro — deux exécutions successives doublaient silencieusement les données (`event_id` n'étant pas seedé, les doublons ne se détectaient pas par `event_id`). Corrigé par un `shutil.rmtree(out_dir)` en début de run. Les chiffres cités dans `docs/audit_legacy.md` (jalon 2) reflètent l'ancien volume doublé — le mécanisme de chaque défaut reste valide, seuls les totaux exacts étaient x2.


