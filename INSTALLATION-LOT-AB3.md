# Lot AB.3 — Checkpoint Git V1

## Objectif

Figer la version actuellement validée de COREF Logistique avant toute nouvelle
évolution.

Le checkpoint inclut notamment :
- migrations Alembic jusqu'à `0038` ;
- lots P → Z ;
- consolidation AA / AA.1 ;
- corrections de tests AB.1 ;
- sécurisation progressive AB.2 ;
- frontend et backend actuellement validés.

## Sécurité du processus

Avant tout commit, le script exige :
1. un dépôt Git valide ;
2. une suite Pytest entièrement verte ;
3. un backend joignable ;
4. une migration Alembic accessible.

Le script :
- supprime uniquement les rapports Pytest générés localement ;
- exécute `git add -A` ;
- crée le commit :

```text
release: consolidate COREF Logistique V1
```

- crée le tag local annoté :

```text
v1.0.0-rc1
```

## Aucun push automatique

Le script **ne pousse rien vers GitHub**.

C'est volontaire : on vérifie d'abord le checkpoint local, puis on fera le push
de la branche et du tag dans AB.3.1.

## Installation

Extraire à la racine du projet en remplaçant `.gitignore`, puis lancer :

```powershell
powershell -ExecutionPolicy Bypass -File .\CREER-CHECKPOINT-GIT-V1.ps1
```

Ensuite :

```powershell
powershell -ExecutionPolicy Bypass -File .\VERIFIER-CHECKPOINT-GIT-V1.ps1
```

## Résultat attendu

Pytest doit être vert.

Git doit montrer un dernier commit :

```text
release: consolidate COREF Logistique V1
```

et le tag :

```text
v1.0.0-rc1
```

L'idéal est ensuite :

```text
nothing to commit, working tree clean
```

ou uniquement quelques fichiers locaux volontairement non suivis/ignorés.

## Étape suivante

Après validation du résultat, AB.3.1 poussera proprement :
- la branche courante ;
- le tag `v1.0.0-rc1`.

Aucune modification de base de données n'est réalisée par AB.3.
