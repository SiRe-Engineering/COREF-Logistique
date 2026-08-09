# Lot 14.3 — Refonte de la liste des préparations

## Présentation

La vue en cartes est remplacée par un tableau cohérent avec l'onglet Affaires.

Colonnes :

- Code préparation ;
- Affaire ;
- Client ;
- Site / Zone ;
- Demandeur ;
- Préparateur ;
- Début ;
- Fin prévue ;
- Avancement ;
- Statut.

Le clic sur une ligne conserve le panneau latéral existant avec l'édition,
les réservations, la suppression et le workflow de préparation.

## Installation

Remplacer :

- `backend/app/schemas/preparation.py`
- `frontend/app/preparations/page.tsx`
- `frontend/app/preparations/page.module.css`

Puis :

```powershell
docker compose restart backend frontend
```

Si nécessaire :

```powershell
docker compose up --build -d backend frontend
```

Aucune migration de base de données n'est nécessaire.

## Test

1. Ouvrir `http://localhost:3000/preparations`.
2. Vérifier l'affichage en tableau.
3. Vérifier les champs Client, Site / Zone, Demandeur et Préparateur.
4. Tester le filtre par statut et la recherche.
5. Cliquer sur une ligne : le panneau d'édition doit toujours fonctionner.
6. Vérifier la barre d'avancement lors de la saisie des quantités préparées.

## Git

```powershell
git add backend/app/schemas/preparation.py frontend/app/preparations
git commit -m "refactor: align preparations list with business cases"
git push
```
