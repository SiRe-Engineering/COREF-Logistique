# Préparations V3 — Lot C valide

Ce correctif annule entièrement le précédent Lot C défectueux.

## Cause corrigée

Le précédent ZIP avait ajouté une seconde implémentation du remplacement par-dessus
celle déjà présente dans la base stable :

- modèle `RemplacementPreparation` supplémentaire ;
- import `Boolean` manquant ;
- nouvelle migration `0022` inutile ;
- seconde fonction `transferer_reservation_remplacement` avec une signature
  incompatible ;
- endpoint de remplacement dupliqué.

La base transmise contenait déjà le flux cohérent suivant :

```text
proposer un remplacement
accepter ou refuser
transférer atomiquement la réservation
conserver la demande et la proposition dans la ligne
```

Ce pack restaure cette implémentation.

## Installation

### 1. Copier le contenu de l’archive à la racine

Les fichiers suivants seront restaurés :

```text
backend/app/api/preparations.py
backend/app/models/preparation.py
backend/app/schemas/preparation.py
backend/app/services/reservations.py
frontend/app/preparations/page.tsx
frontend/app/preparations/page.module.css
```

### 2. Supprimer la migration défectueuse

Depuis PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALLER-LOT-C-VALIDE.ps1
```

Ou manuellement :

```powershell
Remove-Item `
  backend\alembic\versions\0022_add_preparation_replacement_history.py `
  -ErrorAction SilentlyContinue
```

La migration `0022` n’a normalement pas été appliquée, puisque le chargement des
modèles échouait avant l’exécution d’Alembic.

### 3. Reconstruire

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

## Vérifications

```powershell
docker compose ps
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Alembic doit rester sur la révision qui précédait le mauvais fichier `0022`.

## Recette du remplacement

1. Créer et valider une préparation.
2. Démarrer la préparation.
3. Déclarer une ligne indisponible.
4. Cliquer sur le bouton de proposition de remplacement.
5. Sélectionner l’article, l’emplacement et le lot éventuel.
6. Renseigner la quantité et le commentaire.
7. Accepter le remplacement.
8. Vérifier :
   - ancienne réservation libérée ;
   - nouvelle réservation créée ;
   - stock physique inchangé ;
   - ligne remise à préparer ;
   - proposition et décision visibles.
9. Tester un remplacement avec stock insuffisant : refus sans modification
   partielle des réservations.

## Git après validation

```powershell
git status
git add .
git commit -m "fix: restore stable preparation replacement workflow"
git push
```
