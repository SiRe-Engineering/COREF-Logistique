# COREF Logistique

Application de gestion d'inventaire et de matériel pour COREF.

## Version 0.2

Cette version ajoute :

- le référentiel Articles ;
- la création, la recherche et l'archivage d'articles ;
- les API CRUD FastAPI ;
- la validation des références uniques ;
- les migrations Alembic ;
- la persistance PostgreSQL.

## Démarrage

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Adresses :

- application : http://localhost:3000
- documentation API : http://localhost:8000/docs
- contrôle API : http://localhost:8000/api/health

## Mise à jour depuis la version 0.1

Si la base locale de la version 0.1 ne contient aucune donnée importante, repartir proprement :

```powershell
docker compose down -v
docker compose up --build
```

La suppression du volume est nécessaire ici car le premier prototype créait ses tables sans migrations.

## Git

Travail à réaliser sur la branche :

```powershell
git checkout feature/articles
git add .
git commit -m "feat: add articles module"
git push -u origin feature/articles
```
