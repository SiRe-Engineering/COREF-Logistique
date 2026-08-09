# Lot 07 — Emplacements

## Important

Le fichier `frontend/app/globals.css` fourni dans ce lot contient uniquement
les styles à **ajouter à la fin** du fichier existant. Il ne faut pas remplacer
tout le fichier avec ce seul extrait.

## Installation backend

Copier les fichiers backend puis :

```powershell
docker compose down
docker compose up --build -d
```

Ne pas supprimer le volume PostgreSQL. Alembic appliquera la migration `0004`.

## Installation frontend

Copier :

- `frontend/components/layout/Sidebar.tsx`
- `frontend/app/emplacements/page.tsx`

Puis ajouter le contenu du fichier CSS fourni à la fin de
`frontend/app/globals.css`.

## Vérifications

- http://localhost:8000/docs : section Emplacements
- http://localhost:3000/emplacements
- les dix zones COREF sont présentes
- création d’une case de moule
- code automatique du type `MOU-A-1-E2-B`

## Git

```powershell
git add .
git commit -m "feat: add hierarchical locations module"
git push
```
