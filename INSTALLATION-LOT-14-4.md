# Lot 14.4 — Correctif des réservations

## Cause

La saisie de la quantité préparée appelait le même mécanisme que la modification
du besoin. Le backend libérait puis recréait la réservation, alors que la quantité
demandée, le lot et l'emplacement n'avaient pas changé.

Les préparations créées avant le lot 14.1 pouvaient également posséder une
réservation globale non liée à leurs lignes.

## Correction

- la quantité préparée ne déclenche plus aucun recalcul de réservation ;
- seules les modifications du lot, de l'emplacement source ou de la quantité
  demandée recalculent la réservation ;
- la migration 0013 reconstruit les réservations depuis les préparations actives ;
- les totaux réservés des stocks et des lots sont recalculés.

## Installation

```powershell
docker compose down
```

Remplacer et ajouter les fichiers du lot, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0012 -> 0013
```

## Vérification

Pour la situation montrée :

```text
Physique : 775 kg
Réservé : 200 kg
Disponible : 575 kg
```

Les deux lignes de 100 kg doivent pouvoir recevoir une quantité préparée de
100 kg chacune sans tentative de réservation supplémentaire.

Après redémarrage :

1. ouvrir Stocks et vérifier le détail des deux réservations ;
2. ouvrir la préparation ;
3. saisir 100 kg préparés sur chaque ligne ;
4. cliquer sur Marquer prête ;
5. vérifier l'absence d'erreur.

## Git

```powershell
git add backend/app/api/preparations.py backend/alembic/versions
git commit -m "fix: reconcile preparation reservations"
git push
```
