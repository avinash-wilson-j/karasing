# Jalon 7 — Récap : CI GitHub Actions

## Ce qui a été construit

`.github/workflows/ci.yml`, déclenché sur chaque PR et sur push vers `master` :
1. Checkout + setup Python 3.12.
2. `pip install -r requirements.txt`.
3. `ruff check` (lint) sur `generator`, `legacy`, `models/contracts`.
4. Régénération des données synthétiques (`data/raw/` est gitignoré, chaque run CI repart de zéro).
5. `sqlmesh test` (tests unitaires).
6. `sqlmesh plan --no-prompts --auto-apply` — construit **tout le projet depuis zéro** sur un DuckDB éphémère.

## Bot CI/CD officiel SQLMesh — évalué, écarté

`sqlmesh[github]` propose un bot complet (environnements PR temporaires, déploiement auto,
merge auto) — pensé pour une équipe avec une vraie prod partagée entre PRs. Notre projet n'a
pas cet enjeu (état DuckDB local, éphémère) : un workflow simple suffit, le bot aurait été de
la complexité inutile. Bon candidat pour un ADR au jalon 9.

## Ce que le CI a révélé (le vrai intérêt de ce jalon)

Construire le projet **en une seule fois, depuis zéro**, a cassé trois choses jamais testées
localement (on avait toujours construit les modèles incrémentalement, sur plusieurs jours) :

1. **Dépendance cachée dans un audit.** L'audit custom `fct_song_plays_song_id_exists`
   référence `dims.dim_song`, mais SQLMesh construit son graphe d'exécution à partir du
   `SELECT` du modèle, pas de ses audits — donc rien ne garantissait que `dim_song` soit créé
   avant que l'audit tourne. Fix : `depends_on (dims.dim_song)` déclaré explicitement sur
   `facts.fct_song_plays`.

2. **Le bug epoch de `raw_catalogue_songs`, définitivement réglé.** Ce modèle nous a suivi
   depuis le jalon 3 (contournement systématique via `--start`/`--end` en CLI, jamais
   vraiment résolu). Sur un vrai build à froid non-interactif (`--no-prompts --auto-apply`,
   sans possibilité de forcer les dates en CLI sur un plan prod), le bug est réapparu de façon
   bloquante. Fix définitif : passage en `kind FULL`, glob de tous les fichiers
   (`data/raw/catalogue/*/songs.csv`) avec `snapshot_date` extrait du **nom de fichier**
   (`filename=true` + `regexp_extract`) plutôt que templaté depuis `@start_ds` — exactement
   le pattern déjà validé sur `app_events`. `staging.stg_catalogue_songs` suit en `FULL`
   aussi.

3. **Chemins avec antislash (`\`) au lieu de slash (`/`).** Trois modèles
   (`raw_venues`, `raw_subscriptions`, `raw_catalogue_rights_holders`) avaient des chemins
   écrits avec des antislashs — invisible en local (Windows accepte les deux), bloquant sur
   le runner Linux du CI (antislash = caractère littéral, pas un séparateur). Toujours écrire
   les chemins avec `/` dans le code, quel que soit l'OS de dev.

## Leçon générale du jalon

Un environnement de développement local qui fonctionne ne garantit ni l'ordre de construction
correct, ni la portabilité du code. Le premier vrai test "construction complète depuis zéro,
sur un autre OS" est le CI — c'est précisément sa raison d'être, pas un détail secondaire.
