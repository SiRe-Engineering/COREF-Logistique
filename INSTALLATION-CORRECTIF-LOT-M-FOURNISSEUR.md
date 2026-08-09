# Correctif Lot M — Création fournisseur

Deux corrections sont appliquées.

## Backend

Le code fournisseur était transmis deux fois :

```python
Fournisseur(**p.model_dump(), code=...)
```

or `p.model_dump()` contient déjà `code`.

La création utilise maintenant :

```python
donnees = p.model_dump()
donnees["code"] = p.code.strip().upper()
Fournisseur(**donnees)
```

## Frontend

La requête de création est maintenant protégée par `try/catch`.

Une coupure backend produit donc un toast métier au lieu de l'écran rouge
Next.js `Unhandled Runtime Error`.

## Installation

Remplacer :

```text
backend/app/api/achats.py
frontend/app/achats/page.tsx
```

Puis :

```powershell
docker compose up --build -d backend frontend
```

Vérifier :

```powershell
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=100
```

Puis `Ctrl + F5`.

Aucune migration supplémentaire : la base reste en `0028 (head)`.
