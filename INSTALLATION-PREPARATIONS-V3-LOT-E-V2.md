# Lot E v2 — Retours fondés sur les lignes de préparation

## Correction

La première version du Lot E calculait la quantité retournable uniquement à
partir des mouvements liés à la préparation.

Les expéditions réalisées avant l’ajout de ces liens n’étaient pas retrouvées.
L’interface interprétait alors `0 sortie` comme `tout déjà retourné`.

## Nouvelle source de vérité

Chaque ligne conserve désormais :

```text
quantite_expediee
quantite_retournee
```

Le calcul devient :

```text
retournable = quantite_expediee - quantite_retournee
```

Les mouvements restent l’historique détaillé et la conséquence comptable du
retour.

## Reprise des données existantes

La migration `0022` initialise automatiquement :

```text
quantite_expediee = quantite_preparee
```

pour toutes les lignes appartenant à une préparation déjà `EXPEDIEE`.

Les anciennes préparations deviennent donc immédiatement retournables.

## Interface

Le module est renommé :

```text
Préparations / Retours
```

Une préparation expédiée affiche :

- quantité expédiée ;
- quantité retournée ;
- reste retournable.

## Installation

Après avoir copié le contenu de l’archive à la racine, lancer également :

```powershell
powershell -ExecutionPolicy Bypass -File .\RENOMMER-ONGLET-PREPARATIONS-RETOURS.ps1
```

Ce script renomme de façon ciblée le lien global `/preparations` dans la
navigation lorsqu’il se trouve dans un fichier qui n’était pas inclus dans
l’archive source.

Prérequis :

```text
0021 (head)
```

Puis :

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

## Contrôles

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Résultat attendu :

```text
0022 (head)
```

## Recette

1. Ouvrir une préparation expédiée avant le Lot E.
2. Vérifier que la quantité expédiée est reprise.
3. Enregistrer un retour partiel.
4. Vérifier :
   - stock physique augmenté ;
   - mouvement `RETOUR` créé ;
   - quantité retournée mise à jour ;
   - reste retournable diminué.
5. Recharger l’écran.
6. Vérifier la persistance des trois valeurs.
7. Tenter un dépassement : refus attendu.

## Git

```powershell
git status
git add .
git commit -m "fix: base site returns on shipped preparation quantities"
git push
```
