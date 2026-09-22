# Runbook incident — chute de volume `song_played` (21/01/2026)

## Résumé

Chute de volume des événements `song_played` sur une seule journée (21/01/2026) :
**58 événements** contre ~350-550 les jours voisins (~85-90% de perte). Incident simulé
via `python -m generator --inject-anomaly volume_drop --anomaly-day 20`.

## Détection

Audit non-bloquant `fct_song_plays_volume_anomaly` (`audits/fct_song_plays_volume_anomaly.sql`),
déclenché automatiquement à chaque `sqlmesh plan`/`run` sur `facts.fct_song_plays` — compare le
volume du jour à la moyenne glissante des 7 jours précédents, alerte si chute > 50%.

```
[WARNING] facts.fct_song_plays: 'fct_song_plays_volume_anomaly' audit error: 1 row failed.
```

Le pipeline n'a **pas été bloqué** (audit non-bloquant, choix assumé) — le run continue, mais
le signal est visible dans les logs.

## Diagnostic

```sql
SELECT CAST(played_at AS DATE) AS d, COUNT(*) AS n
FROM facts.fct_song_plays
WHERE played_at BETWEEN '2026-01-15' AND '2026-01-25'
GROUP BY 1 ORDER BY 1;
```

Jour isolé : `2026-01-21` = 58 événements vs. 259-554 les jours autour. Vérification de la
source (`raw.raw_app_events`) : la donnée brute reflétait déjà la sous-volumétrie —
le problème vient de la source, pas du pipeline.

## Correction

1. Source corrigée en amont (régénération sans l'anomalie).
2. Restatement **ciblé sur l'intervalle touché uniquement**, pas tout l'historique :
   ```bash
   sqlmesh plan --restate-model raw.raw_app_events --start 2026-01-21 --end 2026-01-22
   ```
3. Vérification post-correction : 538 événements le 21/01 (cohérent avec les jours voisins),
   audit repassé au vert (`audits ✔4`, plus de `[WARNING]`).

**Piège rencontré pendant la correction** : `--end 2026-01-21` est une borne **exclusive**
sur une colonne timestamp — ça ne couvre aucune heure de la journée elle-même. Il a fallu
`--end 2026-01-22` pour couvrir le 21/01 en entier. Même classe de bug que celui déjà
rencontré sur `fct_song_plays` au jalon 4 (documenté dans `jalon4_recap.md`).

## Prévention

- Garder l'audit **non-bloquant** : un audit bloquant sur `fct_song_plays` aurait arrêté
  le `plan` pour les **29 autres jours sains**, pas juste le jour anormal — mauvais compromis.
- Ajouter un **alerting actif** (ex. webhook Discord/Slack sur échec d'audit) plutôt que de
  compter sur la lecture manuelle des logs — aujourd'hui l'alerte existe mais personne n'est
  notifié activement.
- Étendre l'audit de volume pour couvrir aussi les **pics** (`n > 2 * avg_7d_prior`), pas
  seulement les chutes — un doublon massif d'événements produirait un pic, symétriquement
  dangereux (fausse les métriques à la hausse).
- Seuil de 50% à valider avec plus de recul (historique réel plus long) : point ouvert, pas
  tranché ici.
