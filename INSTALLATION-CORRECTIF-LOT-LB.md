# Correctif Lot L-B — Réapprovisionnement préventif

## Nouvelle règle

Un article est proposé dès que :

`stock disponible <= max(stock minimum, seuil d'alerte)`

Avec stock maximum :
`quantité suggérée = stock maximum - disponible`

Sans stock maximum :
- sous le seuil : quantité nécessaire pour revenir au seuil ;
- exactement au seuil : quantité de sécurité égale au seuil ;
- l'interface affiche `Maxi à définir`.

Exemple validé :
- disponible 10
- mini 10
- maxi 0
- seuil 10
=> suggestion 10 et mention `Maxi à définir`.

La recommandation reste de renseigner un stock maximum pour obtenir une cible
de réapprovisionnement explicite.

## Installation

Remplacer les fichiers du ZIP puis :

```powershell
docker compose up --build -d backend frontend
```

Aucune migration.

Puis `Ctrl + F5`.

## Recette
1. Article : disponible 10, mini 10, maxi 0, seuil 10.
2. Ouvrir Réapprovisionnement.
3. L'article doit apparaître.
4. Maxi affiche `Maxi à définir`.
5. Suggestion = 10.
6. Renseigner ensuite maxi = 20 dans Articles.
7. Actualiser : suggestion = 10.
