# Correctif Lot U.1 — statut matériel prêté

## Correction
Un matériel dont l'état technique est `EN_PRET` est maintenant affiché dans la liste Matériels sous le libellé :

**En déplacement**

`Hors service` reste réservé à l'état technique `HORS_SERVICE`.

Aucune migration Alembic.

## Installation
Copier le contenu du correctif à la racine du projet puis :

```powershell
docker compose up --build -d frontend
docker compose logs frontend --tail=100
```

Puis `Ctrl + F5`.

## Comportement attendu
- DISPONIBLE → Disponible
- EN_PRET → En déplacement
- EN_MAINTENANCE → En maintenance
- HORS_SERVICE → Hors service
