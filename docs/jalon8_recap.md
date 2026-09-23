# Jalon 8 — Récap : option cloud (Pulumi + BigQuery Sandbox)

## Ce qui a été fait

- Compte GCP personnel + projet sandbox créé **sans carte bancaire** (`gcloud projects create`).
- APIs BigQuery + Cloud Resource Manager activées sans facturation.
- Infra provisionnée avec **Pulumi** (`infra/`, Python, backend d'état local `pulumi login --local`) :
  5 datasets BigQuery (`raw`, `staging`, `dim`, `facts`, `marts`).
- SQLMesh configuré avec un second gateway (`bigquery`, auth `oauth` via `gcloud auth
  application-default login` — pas de clé de service account à gérer) et un `state_connection`
  séparé (DuckDB local) puisque BigQuery Sandbox ne supporte pas le DML nécessaire au suivi
  d'état de SQLMesh.
- Un modèle **`SEED`** (kind qu'on n'avait pas encore démontré) déployé et interrogé avec
  succès sur du vrai BigQuery.
- Nettoyage complet : `pulumi destroy` + suppression du projet GCP entier.

## Ce qui a marché

Le modèle `dim.seed_venues` (kind `SEED`, données statiques) s'est déployé et a été requêté
sans problème sur BigQuery — preuve que la chaîne Pulumi → BigQuery → SQLMesh fonctionne de
bout en bout, sans jamais toucher une carte bancaire.

## Ce qui n'a pas marché, et pourquoi (une vraie limite d'architecture, pas un bug)

Tous les modèles `raw.*` ont échoué avec `Table-valued function not found: read_csv_auto` /
`read_json_auto`. Ce sont des fonctions **propres à DuckDB** (lire un fichier local
directement dans une requête SQL) — BigQuery n'a pas d'équivalent direct. En vraie prod
cloud, l'ingestion de fichiers vers BigQuery se ferait via une couche dédiée (`bq load`,
tables externes sur Cloud Storage, ou un job Dataflow), **pas** dans le SQL des modèles
SQLMesh eux-mêmes. Migrer la couche `raw/` pour un vrai déploiement BigQuery serait un
chantier d'architecture à part entière, volontairement hors scope de ce jalon optionnel.

## Concept clé découvert : le `state_connection` de SQLMesh

Par défaut, SQLMesh stocke son propre état (quels modèles existent, leurs empreintes, les
intervalles traités) **dans le même moteur que les données**. Sur DuckDB local, ça passait
inaperçu depuis le jalon 1 (l'état vit discrètement dans `db.db`, schéma `sqlmesh`). Sur
BigQuery Sandbox (sans DML), ça casse — solution : `state_connection` séparé, pointant vers
un moteur qui supporte le DML (ici, un DuckDB local dédié).

**Parallèle direct avec Pulumi/Terraform** : même principe (déclaratif + état qui enregistre
la réalité + `plan`/`preview` qui diffuse les deux), mécanisme différent — Pulumi/Terraform
stockent un fichier d'état séparé (JSON), SQLMesh stocke le sien dans des tables SQL au sein
du moteur de données, sauf configuration contraire.

## Incohérence de nommage relevée (pas corrigée, notée)

Les modèles `dim_venue`/`dim_user`/`dim_song`/`dim_artist` (jalon 4) utilisent le schéma
`dims` (avec un "s"), alors que le dataset Pulumi et le nouveau `seed_venues` utilisent `dim`
(sans "s"). Sans conséquence en local (DuckDB), mais ça aurait cassé un vrai déploiement
BigQuery complet sur ces modèles. À corriger si le projet cloud est repris sérieusement.

## Garde-fous respectés

Alerte carte bancaire : sans objet (sandbox, jamais de facturation liée). Nettoyage complet
en fin de session : `pulumi destroy` puis suppression du projet GCP — aucune ressource
persistante.
