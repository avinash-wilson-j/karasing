# KaraSing — plateforme data (projet portfolio fictif)

> ⚠️ **Projet 100% fictif à but pédagogique.** "KaraSing" n'est pas une entreprise réelle,
> n'a aucun lien avec KaraFun ou toute autre marque existante. Toutes les données
> (utilisateurs, chansons, artistes, bars, réservations, abonnements) sont synthétiques,
> générées par [`generator/`](generator/). Aucun vrai titre, vrai artiste ou vraie donnée
> n'est utilisé.

## Contexte

Ce projet simule la reprise d'une plateforme data construite par un prestataire externe
pour un éditeur fictif d'application de karaoké. Objectif : auditer l'existant, le
fiabiliser progressivement et le faire évoluer avec SQLMesh, sur le modèle d'une mission
réelle de Data Engineer senior.

Construit pour apprendre concrètement SQLMesh, les contrats de données et Pulumi/IaC,
sans les avoir pratiqués en production — voir la section "Ce que ce projet prouve / ne
prouve pas" (à venir).

## Statut

🚧 En construction — jalon 1 (setup) en cours.

## Structure

- `generator/` — générateur de données synthétiques (events app, catalogue, abonnements, bookings bars)
- `legacy/` — pipeline "prestataire" existant, repris tel quel pour audit
- `models/`, `seeds/`, `audits/`, `tests/`, `macros/`, `config.yaml` — projet SQLMesh
- `docs/adr/` — Architecture Decision Records
- `data/raw/` — sorties du générateur (non versionné, régénérable)

## Lancer le projet

_À compléter au fur et à mesure des jalons._
