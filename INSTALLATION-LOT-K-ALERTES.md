# Lot K — Alertes & pilotage logistique

## Objectif

Le Lot H affichait les indicateurs en temps réel.

Le Lot K ajoute un véritable centre d’alertes persistantes avec cycle de vie :

```text
ACTIVE
ACQUITTEE
RESOLUE
```

## Règles V1

### Stock

```text
Disponible <= 0
→ CRITIQUE / RUPTURE
```

```text
0 < Disponible <= max(stock_minimum, seuil_alerte)
→ AVERTISSEMENT
```

### Lots béton

Un lot n’est surveillé que s’il possède encore du stock physique.

```text
Périmé
→ CRITIQUE
```

```text
0 à 30 jours
→ CRITIQUE
```

```text
31 à 60 jours
→ AVERTISSEMENT
```

### Préparations

Date de besoin dépassée :

```text
CRITIQUE
```

Ligne `PARTIELLE`, `INDISPONIBLE` ou `REMPLACEMENT_PROPOSE` :

```text
AVERTISSEMENT
```

### Inventaires

Inventaire `EN_COURS` depuis plus de 7 jours :

```text
AVERTISSEMENT
```

## Acquittement

`Acquitter` signifie :

> l’alerte a été vue et prise en charge.

Cela ne la supprime pas.

Elle passe automatiquement en `RESOLUE` seulement lorsque la cause métier
disparaît réellement.

Si la même anomalie réapparaît après résolution, l’alerte est automatiquement
réouverte.

## Interface

Nouvel onglet :

```text
Alertes
```

Filtres :

- ouvertes ;
- actives ;
- acquittées ;
- résolues ;
- catégorie.

Le tableau de bord affiche également un bandeau lorsqu’il existe des alertes
ouvertes.

## Migration

```text
0026
```

Prérequis :

```text
0025
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

Résultat attendu :

```text
0026 (head)
```

Puis :

```text
Ctrl + F5
```

## Recette

1. Ouvrir `Alertes`.
2. Vérifier les ruptures et stocks sous seuil.
3. Vérifier un lot à moins de 60 jours.
4. Vérifier une préparation en retard.
5. Acquitter une alerte.
6. Vérifier qu’elle reste visible comme `ACQUITTEE`.
7. Corriger la cause métier.
8. Synchroniser.
9. Vérifier le passage automatique à `RESOLUE`.
10. Recréer la même anomalie et vérifier sa réouverture.

## Git

```powershell
git status
git add .
git commit -m "feat: add persistent logistics alerts"
git push
```
