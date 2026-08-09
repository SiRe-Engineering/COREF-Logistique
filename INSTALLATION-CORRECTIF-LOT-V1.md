# Correctif Lot V.1 — Wrench Sidebar

Cause : le Lot V utilise l'icône `Wrench` pour le lien Maintenance matériel,
mais elle n'était pas importée depuis `lucide-react`.

Aucune migration.

Copier le correctif à la racine puis :

```powershell
docker compose up --build -d frontend
docker compose logs frontend --tail=100
```

Puis `Ctrl + F5`.
