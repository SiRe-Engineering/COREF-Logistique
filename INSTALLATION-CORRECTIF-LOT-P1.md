# Correctif Lot P.1 — Livraisons attendues

La zone `Livraisons attendues` inclut maintenant :

- toutes les commandes ouvertes dont la date prévue est dépassée ;
- toutes les commandes ouvertes prévues dans les 30 prochains jours.

Les commandes en retard sont affichées en premier et restent également visibles
dans l'onglet `Retards`.

Une commande disparaît de `Livraisons attendues` uniquement lorsqu'elle n'est
plus ouverte, notamment après passage à `RECUE` ou `ANNULEE`.

## Installation

Remplacer :

```text
backend/app/api/pilotage_achats.py
frontend/app/achats/pilotage/page.tsx
frontend/app/achats/pilotage/page.module.css
```

Aucune migration.

Puis :

```powershell
docker compose up --build -d backend frontend
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
```

Puis `Ctrl + F5`.

Pour ton exemple, `CMD-000002` doit apparaître simultanément dans :

```text
Livraisons attendues
Retards
```

avec une carte visuellement marquée `En retard`.
