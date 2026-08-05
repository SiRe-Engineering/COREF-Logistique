# Lot 08 — Stocks

## Fonctionnalités

- stock par article et emplacement ;
- quantité physique, réservée et disponible ;
- seuils minimum, alerte et maximum ;
- synthèse des alertes et ruptures ;
- saisie initiale ou correction temporaire ;
- page `/stocks`.

## Installation

Arrêter les conteneurs :

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du dépôt en acceptant les
remplacements, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`. Alembic doit appliquer la migration `0005`.

## Contrôles

```powershell
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
```

Ouvrir :

- http://localhost:8000/docs
- http://localhost:3000/stocks

Dans Swagger, une section `Stocks` doit être visible.

## Premier test

1. Ouvrir `Stocks`.
2. Cliquer sur `Définir un stock`.
3. Choisir l’article créé.
4. Choisir `Magasin Principal`.
5. Saisir une quantité physique.
6. Enregistrer.
7. Vérifier la quantité disponible et le statut.

## Git

```powershell
git status
git add .
git commit -m "feat: add stock management module"
git push
```
