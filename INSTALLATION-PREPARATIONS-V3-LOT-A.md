# Préparations V3 — Lot A : validation et réservation

## Périmètre

Ce lot stabilise uniquement :

- création d’une préparation en brouillon ;
- ajout, modification et suppression de lignes en brouillon ;
- validation de la préparation ;
- réservation atomique de toutes les lignes ;
- refus si un stock article ou un stock de lot est insuffisant ;
- libération des réservations lors de la suppression de la préparation.

## Éléments volontairement désactivés dans l’interface

- démarrage de la préparation physique ;
- quantités préparées ;
- remplacements ;
- clôture ;
- expédition.

Ils seront réintroduits dans les lots suivants après validation de cette
fondation.

## Règles

### Brouillon

La préparation et ses lignes sont modifiables. Aucun stock n’est réservé.

### Validation

Le backend verrouille les stocks concernés et tente de réserver chaque ligne
dans une seule transaction.

Si une seule ligne est insuffisante :

- la validation est refusée ;
- toutes les modifications de réservation sont annulées ;
- la préparation reste en brouillon.

Si toutes les lignes sont disponibles :

- les réservations sont créées ;
- les quantités réservées des stocks sont mises à jour ;
- la préparation passe à `VALIDEE` ;
- les lignes ne sont plus modifiables.

### Suppression

La suppression d’une préparation libère ses réservations actives avant de
supprimer ses lignes.

## Installation

Aucune nouvelle migration.

Copier le contenu de l’archive à la racine de la branche
`feature/preparations-v3`, puis :

```powershell
docker compose up --build -d backend frontend
```

## Contrôles techniques

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Le frontend ne doit plus contenir l’erreur :

```text
action is not defined
```

## Checklist fonctionnelle

### Validation réussie

- [ ] Créer une préparation.
- [ ] Ajouter plusieurs lignes.
- [ ] Vérifier article, lot, emplacement et quantité.
- [ ] Relever les quantités réservées avant validation.
- [ ] Cliquer sur `Valider et réserver`.
- [ ] Vérifier le statut `Validée`.
- [ ] Vérifier les quantités réservées article.
- [ ] Pour un béton, vérifier aussi la quantité réservée du lot.
- [ ] Vérifier que les lignes ne sont plus modifiables.

### Stock insuffisant

- [ ] Créer un nouveau brouillon.
- [ ] Demander plus que le disponible sur une ligne.
- [ ] Valider.
- [ ] Vérifier le message de stock insuffisant.
- [ ] Vérifier que la préparation reste en brouillon.
- [ ] Vérifier qu’aucune autre ligne n’est restée réservée.

### Suppression

- [ ] Supprimer une préparation validée avec le compte technique.
- [ ] Vérifier la disparition de la préparation.
- [ ] Vérifier la libération de toutes ses réservations.

## Commit après validation

```powershell
git status
git add .
git commit -m "feat: rebuild preparation validation and reservation foundation"
git push
```
