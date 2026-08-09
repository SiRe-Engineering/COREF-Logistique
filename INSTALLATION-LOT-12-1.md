# Lot 12.1 — Correctif focus formulaire Matériels

Remplacer :

`frontend/app/materiels/page.tsx`

Puis exécuter :

```powershell
docker compose restart frontend
```

Si nécessaire :

```powershell
docker compose up --build -d frontend
```

Le correctif déplace `FormulaireMateriel` hors du composant principal afin
d’éviter son démontage et remontage à chaque frappe.

## Git

```powershell
git add frontend/app/materiels/page.tsx
git commit -m "fix: preserve focus in equipment form"
git push
```
