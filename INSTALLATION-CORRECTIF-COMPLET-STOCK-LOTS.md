# Correctif complet — Stock article et stock lot

Ce pack remplace les corrections manuelles précédentes.

## Fichiers remplacés

```text
frontend/app/stocks/page.tsx
backend/app/api/stocks.py
backend/app/schemas/stock.py
```

Le frontend est reconstruit depuis la dernière version stable fournie.

## Installation

Copier le contenu de l’archive à la racine du projet, puis :

```powershell
docker compose up --build -d backend frontend
```

## Contrôles

```powershell
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
curl.exe http://127.0.0.1:8000/api/health
```

Le frontend doit afficher `Ready` sans erreur de syntaxe.

## Payload attendu

Dans DevTools > Network > stocks > Payload :

```json
{
  "article_id": 4,
  "lot_id": 1,
  "emplacement_id": 2,
  "quantite_physique": 200
}
```

## Test fonctionnel

1. Sélectionner un béton.
2. Choisir son lot.
3. Choisir l’emplacement.
4. Enregistrer la quantité.
5. Vérifier que `lot_id` apparaît dans le payload.
6. Ajouter la ligne à une préparation.
7. Vérifier que la réservation du lot fonctionne.

## Git après validation

```powershell
git status
git add .
git commit -m "fix: restore stock form and synchronize concrete batches"
git push
```
