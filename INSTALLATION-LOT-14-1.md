# Lot 14.1 — Réservations, édition et notifications

## Principales évolutions

- édition des préparations Brouillon, Validée et En préparation ;
- ajout, modification et suppression de lignes ;
- réservation automatique lors de la validation ;
- synchronisation des réservations après modification ;
- détail des réservations dans Stocks ;
- suppression de la saisie libre du champ Réservé ;
- notifications pour le demandeur et le préparateur ;
- espace Notifications dans le tableau de bord.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers à la racine du projet, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0011 -> 0012
```

## Test des réservations

1. Créer une préparation avec un demandeur et un préparateur.
2. Ajouter une ligne de 100 kg.
3. Valider.
4. Ouvrir Stocks :
   - Réservé doit augmenter de 100 kg ;
   - Disponible doit diminuer de 100 kg.
5. Cliquer sur la ligne de stock :
   - la préparation, le demandeur et le motif doivent apparaître.
6. Modifier la commande à 150 kg :
   - Réservé doit passer à 150 kg.
7. Supprimer la ligne :
   - la réservation doit être libérée.

## Test des notifications

1. Ouvrir le tableau de bord.
2. Dans `Utilisateur affiché`, saisir exactement le nom du demandeur.
3. Vérifier la notification de création et de réservation.
4. Saisir exactement le nom du préparateur.
5. Vérifier ses notifications.
6. Marquer une notification comme lue.

## Limite provisoire

L’application ne possède pas encore de connexion utilisateur. L’identité affichée
dans le tableau de bord est donc sélectionnée manuellement et enregistrée dans
le navigateur. Le futur module Utilisateurs/Rôles remplacera ce mécanisme.

## Git

```powershell
git status
git add .
git commit -m "feat: add reservations and preparation notifications"
git push
```
