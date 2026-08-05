# Lot 09 — Mouvements de stock

## Fonctionnalités

- entrées ;
- sorties ;
- transferts ;
- retours ;
- ajustements positifs et négatifs ;
- mise à jour transactionnelle du stock ;
- contrôle du stock disponible ;
- historique immuable ;
- références automatiques `MVT-000001` ;
- interface `/mouvements`.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du dépôt, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`. Alembic appliquera la migration `0006`.

## Contrôles

```powershell
docker compose logs backend --tail=120
docker compose logs frontend --tail=80
```

Ouvrir :

- http://localhost:8000/docs
- http://localhost:3000/mouvements
- http://localhost:3000/stocks

## Scénario de test recommandé

Stock initial :

```text
Magasin Principal
Physique : 1000 kg
Réservé : 500 kg
Disponible : 500 kg
```

1. Créer une entrée de 200 kg vers Magasin Principal.
   Résultat attendu : physique 1200 kg, disponible 700 kg.
2. Créer une sortie de 100 kg depuis Magasin Principal.
   Résultat attendu : physique 1100 kg, disponible 600 kg.
3. Créer un transfert de 200 kg du Magasin Principal vers Zone Chantier.
   Résultat attendu :
   - Magasin Principal : physique 900 kg, disponible 400 kg ;
   - Zone Chantier : physique 200 kg.
4. Tenter une sortie supérieure au disponible.
   Résultat attendu : refus HTTP 409, sans modification du stock.

## Git

```powershell
git status
git add .
git commit -m "feat: add transactional stock movements"
git push
```
