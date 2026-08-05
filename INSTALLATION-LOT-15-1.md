# Lot 15.1 — Correctif d'affichage des erreurs de connexion

## Cause

FastAPI peut renvoyer une liste d'erreurs de validation Pydantic :

```json
{
  "detail": [
    {
      "type": "...",
      "loc": ["body", "email"],
      "msg": "...",
      "input": "..."
    }
  ]
}
```

Le frontend essayait d'afficher directement cette liste d'objets dans React,
ce qui provoquait :

```text
Objects are not valid as a React child
```

## Correction

Le correctif transforme toujours la réponse de l'API en texte lisible avant
de l'afficher dans le formulaire.

## Installation

Remplacer :

```text
frontend/components/auth/AuthProvider.tsx
```

Puis :

```powershell
docker compose restart frontend
```

Si nécessaire :

```powershell
docker compose up --build -d frontend
```

Actualiser ensuite avec `Ctrl + F5`.

## Git

```powershell
git add frontend/components/auth/AuthProvider.tsx
git commit -m "fix: render authentication validation errors safely"
git push
```
