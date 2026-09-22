# Jalon 5 — Récap : tests, audits, détection d'anomalie de volume

## Ce qui a été construit

**Audits sur `facts.fct_song_plays`** (déclarés dans `MODEL(... audits (...))`) :
- `not_null` sur `event_id`, `user_id`, `song_id`, `played_at` (bloquant).
- `unique_values` sur `event_id` (bloquant).
- `fct_song_plays_song_id_exists` — audit custom (`audits/`), cohérence référentielle avec `dim_song`, **non bloquant** (un dim pas encore rafraîchi ne doit pas arrêter le pipeline).
- `fct_song_plays_volume_anomaly` — audit custom, **non bloquant**, compare le volume du jour à la moyenne glissante des 7 jours précédents (seuil retenu : chute de plus de 50%). Détecte uniquement les chutes pour l'instant, pas les pics — à revoir si besoin.

**Tests unitaires** (`tests/`) :
- `test_stg_bookings.yaml` — cas DST été (jalon 3).
- `test_venue_occupancy_daily.yaml` — calcul de `occupancy_rate` sur des réservations fictives.
- `dim_song` (SCD2) vérifié **manuellement** via requêtes DuckDB plutôt que par test unitaire (voir limite ci-dessous).

## Trouvaille marquante : l'audit a attrapé un vrai bug

Le premier `unique_values(event_id)` sur `facts.fct_song_plays` a **échoué avec 36 doublons**. En creusant : le contrat Pydantic (jalon 3) valide le *schéma* de chaque ligne, il ne déduplique rien — et on n'avait jamais implémenté la dédup dans le pipeline SQLMesh lui-même, alors qu'on l'avait pourtant diagnostiquée dès l'audit `legacy/` (Constat 4, jalon 2). L'audit bloquant a empêché ce trou de passer en "prod" silencieusement. Corrigé dans `staging/stg_song_played.py` (`drop_duplicates(subset=["event_id"])`).

C'est la démonstration concrète de la valeur des audits : sans ça, on aurait eu exactement le même défaut que `legacy/`, juste däns un pipeline plus moderne.

## Limite connue : SQLMesh `test` et les modèles `SCD_TYPE_2`

Un test unitaire exécute la **requête du modèle telle quelle** (la logique de sélection/dédup), pas le mécanisme de merge `valid_from`/`valid_to` (qui est appliqué par le moteur d'exécution, hors de portée d'un test unitaire classique). En pratique, on a aussi rencontré une friction du framework de test sur la comparaison des colonnes `valid_from`/`valid_to` (ajoutées automatiquement par `SCD_TYPE_2`) qui n'a pas été résolue proprement malgré plusieurs tentatives — verdict : vérifier ces modèles avec des requêtes manuelles (`sqlmesh fetchdf`) plutôt que forcer un test unitaire dessus. Bon point à mentionner en entretien : savoir reconnaître la limite d'un outil de test plutôt que de s'acharner dessus.

## Piège récurrent, encore une fois

Même leçon que jalons 3 et 4 : après une modification de code (`stg_song_played.py`), il a fallu un `sqlmesh plan` classique (pas `--restate-model`) pour que le changement soit détecté — le cascade s'est ensuite propagé automatiquement à `fct_song_plays` et aux marts qui en dépendent (`Indirectly Modified`).
