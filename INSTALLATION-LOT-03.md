# Lot 03 — Familles et sous-familles

Copier le contenu du lot à la racine du dépôt, puis exécuter :

```powershell
docker compose down
docker compose up --build
```

Il n’est pas nécessaire de supprimer le volume PostgreSQL. Alembic appliquera
automatiquement la migration `0002`.

Vérifications :

- http://localhost:8000/api/health
- http://localhost:8000/docs
- `GET /api/familles`

La réponse doit contenir neuf familles COREF, dont `Moules`.

Puis :

```powershell
git add .
git commit -m "feat: add families and subfamilies reference data"
git push
```
