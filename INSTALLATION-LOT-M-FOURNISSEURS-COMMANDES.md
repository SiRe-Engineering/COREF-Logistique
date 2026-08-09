# Lot M — Fournisseurs & commandes d'achat

## Périmètre V1

- référentiel fournisseurs ;
- commandes fournisseur multi-lignes à partir des besoins ouverts du Lot L ;
- statuts BROUILLON / VALIDEE / ENVOYEE / PARTIELLEMENT_RECUE / RECUE / ANNULEE ;
- réception ligne par ligne, partielle ou totale ;
- traçabilité commande -> ligne -> mouvement de stock ;
- mise à jour du besoin Lot L ;
- entrée stock et recalcul CUMP via le moteur de mouvements existant ;
- infrastructure articles/fournisseurs (référence, tarif, délai, minimum, préféré).

## Migration

`0028_add_suppliers_purchase_orders.py`

## Installation

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

Vérifier :

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Attendu : `0028 (head)`.

Puis `Ctrl + F5`.

## Recette recommandée

1. Créer un fournisseur dans `Fournisseurs / Achats`.
2. Créer ou disposer de deux besoins ouverts dans `Réapprovisionnement`.
3. Créer une commande et cocher un ou plusieurs besoins.
4. Passer la commande de BROUILLON à VALIDEE puis ENVOYEE.
5. Réceptionner partiellement une ligne.
6. Vérifier : commande PARTIELLEMENT_RECUE, besoin Lot L, stock, mouvement, CUMP.
7. Réceptionner le solde de toutes les lignes.
8. Vérifier : commande RECUE.

Pour un article Béton, renseigner l'ID du lot dans la V1 de la fenêtre de réception.

## Git

```powershell
git status
git add .
git commit -m "feat: add suppliers and purchase orders"
git push
```
