# Lot 18.1 — Statuts minimaux des lignes de préparation

## Périmètre strict

Ce lot ajoute uniquement quatre états opérationnels :

```text
A_PREPARER
PREPAREE
PARTIELLE
INDISPONIBLE
```

Le statut `EXPEDIEE` reste conservé pour les lignes déjà expédiées.

Ce lot ne modifie pas :

- la logique de réservation ;
- le stock ;
- les notifications ;
- les mouvements ;
- l’expédition ;
- les remplacements ;
- l’impression.

## Actions disponibles

Pendant une préparation en cours :

| Icône | Action |
|---|---|
| `✓` | Marquer la ligne complète |
| `½` | Déclarer une quantité partielle avec motif obligatoire |
| `!` | Déclarer l’article indisponible avec motif obligatoire |
| `↺` | Remettre la ligne à préparer |

La quantité préparée n’est plus saisie librement dans le tableau.

## Installation

Prérequis :

```text
Git : commit stable 99c2a37
Alembic : 0017
```

Copier tout le contenu de l’archive à la racine du dépôt, puis :

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

## Contrôles techniques

```powershell
docker compose logs backend --tail=200
```

Migration attendue :

```text
Running upgrade 0017 -> 0018
```

Puis :

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs frontend --tail=100
```

Résultats attendus :

```text
0018 (head)
Application startup complete
{"status":"ok","database":"connected","version":"1.0.0"}
```

## Checklist fonctionnelle

- [ ] Créer une préparation avec au moins quatre lignes.
- [ ] Valider la préparation.
- [ ] Démarrer la préparation.
- [ ] Marquer une ligne complète avec `✓`.
- [ ] Vérifier : statut `Préparée`, manquant `0`.
- [ ] Marquer une ligne partielle avec `½`.
- [ ] Vérifier que la quantité partielle est inférieure au besoin.
- [ ] Vérifier que le motif est obligatoire.
- [ ] Marquer une ligne indisponible avec `!`.
- [ ] Vérifier : préparé `0`, manquant égal au demandé.
- [ ] Remettre une ligne à préparer avec `↺`.
- [ ] Vérifier que le motif est effacé.
- [ ] Vérifier que la préparation ne peut pas être marquée prête tant qu’une ligne n’est pas complète.
- [ ] Vérifier les réservations existantes dans Stocks.
- [ ] Vérifier qu’aucun mouvement de stock n’a été créé.

## Commit uniquement après validation

```powershell
git status
git add .
git commit -m "feat: add minimal preparation line statuses"
git push
```

En cas de problème, ne pas committer. Conserver les logs backend et frontend.
