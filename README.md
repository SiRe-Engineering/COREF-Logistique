# COREF Logistique

Socle initial de l'application de gestion d'inventaire et de matériel de COREF.

## Architecture

- `frontend` : Next.js / TypeScript
- `backend` : FastAPI / SQLAlchemy
- `db` : PostgreSQL
- orchestration locale : Docker Compose

## Démarrage

1. Copier le fichier d'environnement :

```bash
cp .env.example .env
```

Sous PowerShell :

```powershell
Copy-Item .env.example .env
```

2. Lancer l'application :

```bash
docker compose up --build
```

3. Ouvrir :

- Application : http://localhost:3000
- Documentation API : http://localhost:8000/docs
- État de l'API : http://localhost:8000/api/health

## Arrêt

```bash
docker compose down
```

Pour supprimer également la base locale :

```bash
docker compose down -v
```

## Première version du domaine

Le socle contient déjà les entités suivantes :

- articles ;
- emplacements ;
- mouvements de stock.

Les tables sont créées automatiquement au démarrage pour faciliter le prototypage. Avant la mise en production, cette création automatique sera remplacée par des migrations Alembic.

## Commandes Git suggérées

```bash
git add .
git commit -m "feat: initialise application stack"
git push
```
# COREF-Logistique
Application de gestion des matériaux et matériels
