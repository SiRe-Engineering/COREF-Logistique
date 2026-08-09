# Lot N — Fournisseurs avancés & tarifs articles

## Nouveautés

### Référentiel article / fournisseur

Nouvelle page :

```text
Fournisseurs / Achats → Tarifs articles
```

Pour chaque association :

- référence fournisseur ;
- prix unitaire HT ;
- délai d’approvisionnement ;
- minimum de commande ;
- fournisseur préféré ;
- date de mise à jour du prix.

Un seul fournisseur peut être marqué `préféré` par article.

### Historique de prix

Chaque modification de prix crée une ligne historisée avec :

- ancien contexte temporel ;
- nouveau prix ;
- utilisateur ;
- commentaire de modification.

La migration reprend également les tarifs déjà présents depuis le Lot M.

### Lot L — Réapprovisionnement

Les suggestions affichent maintenant automatiquement :

- fournisseur préféré ;
- référence fournisseur ;
- prix conseillé ;
- délai.

Lors de la création du besoin, le fournisseur préféré et son tarif sont
repris automatiquement.

### Lot M — Commandes

Quand une commande est créée pour un fournisseur déjà associé à l’article :

- le tarif fournisseur enregistré est utilisé ;
- la référence fournisseur est reprise ;
- le minimum de commande est appliqué si nécessaire.

La réception reste reliée au même moteur de stock et de CUMP.

## Migration

```text
0029
```

Prérequis :

```text
0028
```

## Installation

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

Puis :

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Attendu :

```text
0029 (head)
```

Puis `Ctrl + F5`.

## Recette

1. Ouvrir `Fournisseurs / Achats`.
2. Cliquer `Tarifs articles`.
3. Associer un fournisseur à un article.
4. Renseigner référence fournisseur, prix, délai et minimum.
5. Le passer fournisseur préféré.
6. Modifier le prix et vérifier l’historique.
7. Placer l’article au seuil de réapprovisionnement.
8. Vérifier que le Lot L propose automatiquement fournisseur, prix et délai.
9. Créer le besoin : vérifier que fournisseur et prix sont préremplis.
10. Créer une commande dans le Lot M avec ce fournisseur.
11. Vérifier que le tarif et la référence fournisseur sont repris.
12. Réceptionner et vérifier stock + CUMP.

## Git

```powershell
git status
git add .
git commit -m "feat: add supplier article tariffs and price history"
git push
```
