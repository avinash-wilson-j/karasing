# Audit du pipeline legacy — KaraSing

Auteur : Wilson
Date : 21/09/2026
Périmètre : `legacy/run_all.py` + `legacy/sql/*.sql`, exécuté sur un run `python -m generator --days 30 --seed 42`.

## Méthode

Lecture du legacy, 
comparaison avec reporting, 
exploiratory data analysis


## Constat 1 — Conversion UTC/local incorrecte

- **Fichier** : `legacy/sql/02_venue_occupancy.sql`
- **Ligne** : 8-9 (`CAST(slot_start AS TIMESTAMP) + INTERVAL 1 HOUR`)
- **Problème** : `slot_start`/`booked_at` sont fournis en heure locale naïve (sans fuseau) par la source `bookings.csv`. Le pipeline ajoute une heure comme s'il convertissait de l'UTC vers le local, ce qui décale en réalité une heure déjà locale.
- **Impact concret** : Décalage à lendemain sur les slots booké pour 23h
- **Classification (dette acceptable / vrai risque)** : vrai risque
- **Justification** : Réservations basculent sur le mauvais jour
- **Correction proposée** : CAST(slot_start AS TIMESTAMP) AT TIME ZONE 'Europe/Paris' AS slot_start_utc

## Constat 2 — Comptage des utilisateurs actifs sur un champ interne non fiable

- **Fichier** : `legacy/sql/03_active_users.sql`
- **Ligne** : 6-7 (`COUNT(DISTINCT _client_seq)`)
- **Problème** : `_client_seq` est un compteur interne du SDK mobile qui redémarre à 1 à chaque session. Il n'identifie pas un utilisateur de façon unique sur l'ensemble du dataset.
- **Impact concret** :  COUNT(DISTINCT _client_seq) et COUNT(DISTINCT user_id) sur raw_app_events (event_type='song_played'), donne différents chiffres. 
- **Classification (dette acceptable / vrai risque)** : vrai risque
- **Justification** : champ interne non fiable 11 _client_seq vs 598 user_id
- **Correction proposée** : remplacer _client_seq par user_id

## Constat 3 — `INNER JOIN` sur les artistes : chansons sans artiste invisibles

- **Fichier** : `legacy/sql/01_top_songs.sql`
- **Ligne** : 9-10 (`JOIN latest_artists a ON a.artist_id = s.artist_id`)
- **Problème** : les chansons sans `artist_id` (musique traditionnelle, domaine public — environ 4% du catalogue) sont totalement absentes de `reporting.top_songs`, alors qu'elles ont bien été écoutées.
- **Impact concret** :  SUM(play_count) avec INNER JOIN vs avec LEFT JOIN montre des écarts
- **Classification (dette acceptable / vrai risque)** : vrai risque
- **Justification** : chansons des artistes inconnus invisibles 25798 sans artists vs 24698 avec artists
- **Correction proposée** : Faire un left join avec artist et utiliser coalesce

## Constat 4 — Doublons d'événements non dédupliqués

- **Fichier** : `legacy/sql/01_top_songs.sql`
- **Ligne** : 4-13 (`COUNT(*)` sans dédoublonnage sur `event_id`)
- **Problème** : `raw_app_events` contient un petit pourcentage d'événements dupliqués (même `event_id` répété). Le `COUNT(*)` actuel les compte comme des écoutes distinctes.
- **Impact concret** : Le nb d'évenements distincts par activité d'user sont des fois en doublons
- **Classification (dette acceptable / vrai risque)** : Risque mineur
- **Justification** : Doublons event_id non dédupliqués (~0,3%)
- **Correction proposée** : Colonne event_id, Group by à ajouter

## Constat 5 — Full refresh à chaque exécution

- **Fichier** : `legacy/run_all.py`
- **Ligne** : `DB_PATH.unlink()` avant chaque run
- **Problème** : tout l'historique est retraité à chaque exécution, sans incrémentalité.
- **Impact concret** : Pas un bug aujourd'hui (petit volume) 
- **Classification (dette acceptable / vrai risque)** : Dette acceptable
- **Justification** : Pas d'historique des données
- **Correction proposée** : Migration

## Constat 6 — Aucun test ni audit automatisé

- **Fichier/périmètre** : tout `legacy/`
- **Problème** : aucun test unitaire, aucun contrôle de cohérence/fraîcheur/non-régression. Une régression (ex. réintroduction du bug du Constat 3) ne serait détectée que par une relecture manuelle du SQL.
- **Impact concret** : Perte de données en prod non identifiable sans test/audit/contrôle
- **Classification (dette acceptable / vrai risque)** : vrai risque
- **Justification** : On saura pas si les chiffres sont faux
- **Correction proposée** : Migration avec QD

## Constat 7 — Absence de séparation de couches (schéma)

- **Fichier** : `legacy/run_all.py`
- **Problème** : les vues brutes (`raw_app_events`, `latest_songs`...) et les tables de reporting ne sont pas séparées par schéma (`raw` vs `reporting`).
- **Impact concret** : Perte d'organisation/uniticité
- **Classification (dette acceptable / vrai risque)** : Dette technique
- **Justification** : A faire pour bien cadrer le flux de données
- **Correction proposée** : Créer une BDD bien structurée en ODS, Socle, Reporting

## Priorisation

Si tu ne pouvais corriger qu'**un seul** de ces constats avant la prochaine mise en prod du rapport, lequel choisis-tu et pourquoi ?

1 le enjeux operationel est trop grand.

Classe les 7 constats du plus urgent au moins urgent :

1. Comptage des utilisateurs actifs sur un champ interne non fiable  
2. Conversion UTC/local incorrecte
3. Chansons sans artiste invisibles
4. Doublons d'événements non dédupliqués
5. Aucun test ni audit automatisé
6. Absence de séparation de couches
7. Full refresh à chaque exécution

