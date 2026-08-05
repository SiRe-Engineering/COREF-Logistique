# Lot 10 — Traçabilité des bétons

## Ce lot ajoute

- lots fournisseurs de béton ;
- fabrication et péremption ;
- fournisseur ;
- références certificat et FDS ;
- stock par lot et emplacement ;
- lot obligatoire dans les mouvements de béton ;
- contrôle du disponible par lot ;
- proposition FEFO ;
- page `/lots-beton`.

## Conservation des données existantes

La migration `0007` crée automatiquement un lot fournisseur technique
`LOT-INITIAL` pour chaque article Béton existant et y reprend les quantités
physiques et réservées déjà enregistrées.

Aucune donnée de stock n’est supprimée.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du dépôt, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

## Contrôles

```powershell
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

La migration attendue est :

```text
Running upgrade 0006 -> 0007
```

Ouvrir :

- http://localhost:8000/docs
- http://localhost:3000/lots-beton
- http://localhost:3000/mouvements

## Test recommandé

1. Vérifier la présence du lot `LOT-INITIAL` associé au béton existant.
2. Créer un nouveau lot fournisseur avec ses dates.
3. Créer une entrée de béton en sélectionnant ce nouveau lot.
4. Vérifier que le mouvement affiche le numéro du lot.
5. Tenter une sortie sans lot via Swagger : la requête doit être refusée.
6. Tenter une sortie supérieure au disponible du lot : refus HTTP 409.

## Git

```powershell
git status
git add .
git commit -m "feat: add concrete batch traceability"
git push
```
