# Lot 02 — Fondation V1 et API Articles

Copier le contenu de cette archive à la racine du dépôt en acceptant
le remplacement des fichiers.

## Redémarrage propre

```powershell
docker compose down -v
docker compose up --build
```

## Contrôles

- http://localhost:8000/api/health
- http://localhost:8000/docs
- GET http://localhost:8000/api/articles

La réponse de santé attendue est :

```json
{
  "status": "ok",
  "database": "connected",
  "version": "1.0.0"
}
```

## Premier article depuis Swagger

Dans `/docs`, ouvrir `POST /api/articles`, puis utiliser :

```json
{
  "reference": "OUT-MEU-001",
  "designation": "Meuleuse angulaire 125 mm",
  "famille": "Outillage",
  "sous_famille": "Électroportatif",
  "unite": "unité",
  "stock_minimum": 2
}
```
