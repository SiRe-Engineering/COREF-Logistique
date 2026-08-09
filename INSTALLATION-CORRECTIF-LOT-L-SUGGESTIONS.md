# Correctif Lot L — Suggestions de réapprovisionnement

## Cause

La requête de suggestions faisait :

```text
SELECT Article + SUM(Stock)
GROUP BY Article.id
```

Or `Article` charge automatiquement ses relations `famille` et
`sous_famille`. SQLAlchemy ajoutait donc ces tables au SELECT et PostgreSQL
refusait la requête car leurs colonnes n'étaient pas présentes dans le
`GROUP BY`.

Erreur observée :

```text
psycopg.errors.GroupingError:
column "familles_1.id" must appear in the GROUP BY clause
```

## Correction

Les quantités de stock sont maintenant agrégées dans une sous-requête par
`article_id`, puis jointes aux articles. La requête principale n'a donc plus
besoin de `GROUP BY`.

Aucune migration n'est nécessaire. La base doit rester en :

```text
0027 (head)
```

## Installation

Remplacer :

```text
backend/app/services/reapprovisionnement.py
```

Puis :

```powershell
docker compose up --build -d backend
docker compose logs backend --tail=100
```

Faire ensuite `Ctrl + F5` dans le navigateur.

## Vérification

La route `/api/reapprovisionnement/suggestions` doit répondre 200 lorsqu'elle
est appelée par l'application authentifiée.

Un `curl` sans jeton continuera normalement à répondre `401
Authentification requise` : ce comportement est attendu.
