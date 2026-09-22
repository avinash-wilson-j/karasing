# Jalon 4 — Récap : dims SCD2, faits incrémentaux, marts

## Ce qui a été construit

**Dimensions (`models/dims/`)** :
- `dims.dim_venue` — `FULL`, simple (les bars changent rarement, pas de SCD2).
- `dims.dim_user` — `SCD_TYPE_2_BY_TIME` (`unique_key user_id`, `updated_at_name recorded_at`), sourcé sur `staging.stg_subscriptions`.
- `dims.dim_artist` — `SCD_TYPE_2_BY_COLUMN` (surveille `name`, `country`), sourcé sur `raw.raw_catalogue_artists`.
- `dims.dim_song` — `SCD_TYPE_2_BY_COLUMN` (surveille `title`, `artist_id`, `genre`, `language`, `release_year`, `licensed_until`, `rights_holder_id`), sourcé sur `staging.stg_catalogue_songs`.

**Faits (`models/facts/`)** :
- `facts.fct_song_plays` — `INCREMENTAL_BY_TIME_RANGE` (`time_column played_at`), depuis `staging.stg_song_played` (déjà validé par le contrat).
- `facts.fct_bar_bookings` — `FULL`, depuis `staging.stg_bookings`.
- `facts.fct_subscription_events` — `FULL`, tout l'historique de changements (contrairement au dim, le fait garde chaque événement).

**Marts (`models/marts/`)** :
- `marts.top_songs_by_country_day` — écoutes par pays/jour/chanson, avec jointure `dim_song` + `dim_artist`.
- `marts.royalties_monthly` — redevances mensuelles par ayant droit (`raw.raw_catalogue_rights_holders` × taux × écoutes).
- `marts.subscription_kpis_monthly` — actifs/résiliés par mois et par plan (version simple, pas encore un vrai taux de churn).
- `marts.venue_occupancy_daily` — taux d'occupation des bars (capacité codée en dur depuis les constantes du générateur : nombre de salles × 7 créneaux/jour).

## Concepts SQLMesh démontrés

| Concept | Où |
|---|---|
| `SCD_TYPE_2_BY_TIME` vs `SCD_TYPE_2_BY_COLUMN` | `dim_user` vs `dim_artist`/`dim_song` |
| `disable_restatement` (protection par défaut des tables historisées) | tous les SCD2 |
| Jointure "point-in-time" sur un dim SCD2 (`valid_to IS NULL` pour la version courante) | toutes les marts qui joignent `dim_song`/`dim_artist` |
| Bornes `start`/`end` sur colonne `TIMESTAMP` vs `DATE` | `fct_song_plays` |

## Pièges rencontrés (à retenir pour l'entretien)

1. **`SCD_TYPE_2` attend l'état courant, pas un historique complet en une fois.** La requête source doit renvoyer une ligne par clé (état "aujourd'hui"), et SQLMesh construit l'historique **au fil des runs successifs**, en comparant à ce qui est déjà matérialisé — pas en rejouant un log de changements fourni d'un coup. On a dû dédupliquer `stg_subscriptions`/`stg_catalogue_songs` avec un `QUALIFY ROW_NUMBER() ... = 1` avant de les passer au SCD2. Conséquence : l'historique qu'on connaissait déjà avant le premier `plan` n'est pas reconstruit avec les vraies dates (`valid_from` = epoch, un sentinel "depuis toujours, on ne sait pas exactement quand").
2. **`disable_restatement TRUE` par défaut sur `SCD_TYPE_2`** — protection volontaire contre la perte de données sur une table historisée. Pour itérer en dev, on l'a désactivé temporairement (`disable_restatement false`), à remettre à `true` une fois le modèle stabilisé.
3. **`--restate-model` ne relit pas le code s'il a changé** — confirmé une nouvelle fois sur `dim_user` et `fct_song_plays`. Toujours faire un `sqlmesh plan` classique d'abord pour que le changement de fichier soit détecté, *puis* un restatement si besoin.
4. **Borne `end` sur une colonne `TIMESTAMP` avec macros `@start_ds`/`@end_ds`** : `end '2026-01-30'` exclut tout ce qui se passe après minuit ce jour-là (`@end_ds` = `'2026-01-30 00:00:00'`). Il a fallu repousser à `'2026-01-31'` pour couvrir la journée entière — `fct_song_plays` perdait silencieusement 290 lignes (tout le 30/01) avant la correction.

## Limite connue, assumée pour l'instant

`marts.subscription_kpis_monthly` compte actifs/résiliés par mois mais ne calcule pas encore un vrai **taux de churn** (qui nécessiterait : actifs en début de période, résiliés pendant la période, `churn_rate = résiliés / actifs_debut_periode`). À affiner si le temps le permet, sinon à documenter comme limite connue dans le README final.
