# Lot K-B — Édition des articles

Le backend possédait déjà `PATCH /api/articles/{id}` et les champs nécessaires.
Ce correctif ajoute donc l’interface d’édition sans migration SQL.

## Champs modifiables

- référence ;
- désignation ;
- famille ;
- sous-famille ;
- unité ;
- stock minimum ;
- seuil d’alerte ;
- stock maximum.

Le CUMP reste volontairement dans sa commande dédiée.

## Alertes

Le Lot K utilise :

```text
max(stock_minimum, seuil_alerte)
```

La modification de ces paramètres est donc prise en compte lors de la
prochaine synchronisation du centre d’alertes.

## Installation

```powershell
docker compose down
docker compose up --build -d
```

Puis :

```powershell
curl.exe http://127.0.0.1:8000/api/health
docker compose logs frontend --tail=100
```

Faire `Ctrl + F5`.

## Recette

1. Articles.
2. Ouvrir un article.
3. Cliquer `Modifier l’article`.
4. Modifier le stock minimum et le seuil d’alerte.
5. Enregistrer.
6. Fermer/réouvrir l’article et vérifier les valeurs.
7. Ouvrir `Alertes` et cliquer `Synchroniser`.
8. Tester également famille/sous-famille et unité.

## Git

```powershell
git status
git add .
git commit -m "feat: add article editing interface"
git push
```
