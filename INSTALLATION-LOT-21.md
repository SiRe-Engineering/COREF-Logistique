# Lot 21 — Suppressions techniques sans justification

Actions réservées à `ADMINISTRATEUR_TECHNIQUE`.

Aucun motif n’est demandé. Une confirmation simple reste affichée.

## Stocks

Suppression autorisée si aucune réservation active n’existe. Pour les bétons,
les détails `StockLot` du même article et emplacement sont supprimés aussi.

## Préparations

Suppression autorisée quel que soit le statut. Les réservations actives sont
libérées et les notifications liées sont supprimées.

## Affaires

Suppression autorisée seulement lorsqu’il ne reste plus de préparation ni de
mouvement de stock actif.

## Installation

Prérequis : lot 20 installé, Alembic `0020`.

```powershell
docker compose up --build -d backend frontend
```

## Vérification

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Alembic doit rester en `0020 (head)`.

## Git après validation

```powershell
git status
git add .
git commit -m "feat: add technical deletion of stocks preparations and cases"
git push
```
