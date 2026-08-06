# Préparations V3 — Lot C : remplacements

## Fonctions

- bouton de remplacement sur une ligne `INDISPONIBLE` ;
- choix d’une autre référence ;
- choix de l’emplacement ;
- choix du lot pour un béton ;
- contrôle du stock disponible ;
- transfert atomique de la réservation ;
- conservation de l’historique des remplacements ;
- remise de la ligne à `A_PREPARER`.

## Stock

Le stock physique n’est jamais modifié.

Seules les quantités réservées sont transférées.

## Migration

```text
0022
```

## Installation

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

## Vérification

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

## Recette

1. Créer et valider une préparation.
2. Démarrer la préparation.
3. Déclarer une ligne indisponible.
4. Cliquer sur `↻`.
5. Choisir un autre article.
6. Choisir emplacement et lot éventuel.
7. Vérifier :
   - réservation initiale libérée ;
   - nouvelle réservation créée ;
   - stock physique inchangé ;
   - ligne remise à préparer ;
   - historique visible.
8. Tester une quantité supérieure au disponible : refus attendu.
9. Refaire un second remplacement et vérifier l’historique complet.

## Git

```powershell
git status
git add .
git commit -m "feat: add preparation replacement workflow"
git push
```
