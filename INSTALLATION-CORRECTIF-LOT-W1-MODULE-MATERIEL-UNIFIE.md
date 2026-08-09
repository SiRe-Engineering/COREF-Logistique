# Correctif Lot W.1 — Module Matériels unifié

## Objectif

Le menu gauche n'affiche plus séparément :

- Matériels
- Prêts matériel
- Maintenance matériel
- Documents matériel

Il ne conserve qu'une seule entrée :

```text
Matériels
```

## Navigation interne

Toutes les pages du module affichent maintenant les mêmes sous-onglets :

```text
Parc matériel
Prêts & déplacements
Maintenance & contrôles
Documents & conformité
```

Les routes techniques existantes sont conservées :

```text
/materiels
/prets-materiel
/maintenance-materiel
/documents-materiel
```

Cela évite toute régression ou modification backend.

## Installation

Aucune migration.

Copier le correctif à la racine du projet puis :

```powershell
docker compose up --build -d frontend
docker compose logs frontend --tail=100
```

Puis :

```text
Ctrl + F5
```

## Résultat attendu

Dans le menu gauche :

```text
Matériels
```

En ouvrant ce module, une barre de navigation interne permet de passer entre
le parc, les prêts, la maintenance et les documents sans encombrer le menu
principal.
