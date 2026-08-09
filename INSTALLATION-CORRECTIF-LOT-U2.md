# Correctif Lot U.2 — Affichage "En déplacement"

## Cause exacte

La page `Matériels` utilise la fonction :

```text
statutMateriel(etat)
```

Tout état non explicitement reconnu tombait dans le cas par défaut
`Hors service`.

`EN_PRET` n'était pas traité dans cette fonction, donc un matériel
correctement passé à `EN_PRET` par le Lot U était affiché à tort
`Hors service`.

## Correctif

`EN_PRET` est maintenant reconnu explicitement et affiché :

```text
En déplacement
```

Il est également ajouté dans la liste des états connus de la page.

Aucune migration.

## Installation

Remplacer uniquement :

```text
frontend/app/materiels/page.tsx
```

Puis :

```powershell
docker compose up --build -d frontend
docker compose logs frontend --tail=100
```

Enfin :

```text
Ctrl + F5
```

## Résultat attendu

- DISPONIBLE → Disponible
- EN_CHANTIER → En chantier
- EN_PRET → En déplacement
- EN_MAINTENANCE → Maintenance
- HORS_SERVICE → Hors service
- PERDU → Perdu
