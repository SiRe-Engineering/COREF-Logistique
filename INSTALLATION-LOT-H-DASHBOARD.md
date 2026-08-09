# Lot H — Tableau de bord logistique & alertes

## Objectif

Transformer la page d’accueil en écran de pilotage quotidien.

## KPI

- articles actifs ;
- ruptures de stock ;
- articles sous seuil ;
- lots béton à échéance dans les 60 jours ;
- préparations à traiter ;
- préparations en retard ;
- inventaires en cours ;
- lignes expédiées avec quantité non encore retournée.

## Blocs opérationnels

### Préparations

Affiche les préparations actives avec :

- échéance ;
- retard ;
- nombre de lignes bloquées.

### Stock

Une rupture correspond à :

```text
stock disponible <= 0
```

Une alerte sous seuil correspond à :

```text
0 < stock disponible <= seuil_alerte
```

Si `seuil_alerte` vaut zéro, `stock_minimum` est utilisé.

### Lots béton

Horizon :

```text
60 jours
```

Niveaux :

```text
PÉRIMÉ      < 0 jour
CRITIQUE    0 à 30 jours
À SURVEILLER 31 à 60 jours
```

Les lots sans stock physique ne sont pas remontés.

### Inventaires

Affiche la progression des inventaires `EN_COURS`.

## Notifications

Le bloc existant de notifications utilisateur est conservé sous le tableau de
bord.

## Migration

Aucune migration.

## Installation

```powershell
docker compose up --build -d backend frontend
```

Puis :

```text
Ctrl + F5
```

## Vérification

```powershell
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

## Recette

1. Ouvrir le tableau de bord.
2. Vérifier les KPI.
3. Vérifier qu’un article à stock disponible nul apparaît en rupture.
4. Vérifier un article sous son seuil.
5. Vérifier un lot béton périmant dans moins de 60 jours.
6. Vérifier une préparation dont `date_besoin` est dépassée.
7. Vérifier un inventaire en cours.
8. Vérifier que les notifications personnelles sont toujours présentes.

## Git

```powershell
git status
git add .
git commit -m "feat: add logistics dashboard and alerts"
git push
```
