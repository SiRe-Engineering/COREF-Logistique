# Lot 14.2 — Suppression des préparations

## Fonctionnement

Une préparation peut être supprimée aux statuts :

- Brouillon ;
- Validée ;
- En préparation ;
- Prête.

Une préparation `EXPEDIEE` ne peut pas être supprimée afin de conserver
la traçabilité des sorties de stock.

Lors de la suppression :

1. les réservations actives sont libérées ;
2. les quantités réservées du stock et des lots sont recalculées ;
3. les lignes de préparation sont supprimées ;
4. le demandeur et le préparateur reçoivent une notification ;
5. la préparation disparaît de l'interface.

## Installation

Remplacer :

- `backend/app/api/preparations.py`
- `frontend/app/preparations/page.tsx`

Puis exécuter :

```powershell
docker compose restart backend frontend
```

Si nécessaire :

```powershell
docker compose up --build -d backend frontend
```

Aucune migration de base de données n'est nécessaire.

## Test

1. Créer ou ouvrir une préparation validée avec une réservation active.
2. Vérifier la quantité réservée dans Stocks.
3. Cliquer sur `Supprimer la préparation`.
4. Confirmer.
5. Vérifier :
   - la disparition de la préparation ;
   - la libération de la réservation ;
   - la mise à jour du disponible ;
   - les notifications du demandeur et du préparateur.
6. Vérifier qu'une préparation expédiée ne présente pas le bouton de suppression.

## Git

```powershell
git add backend/app/api/preparations.py frontend/app/preparations/page.tsx
git commit -m "feat: allow preparation deletion and release reservations"
git push
```
