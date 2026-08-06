# Préparations V3 — Lot E : retours chantier

## Fonctions

Depuis une préparation `EXPEDIEE`, l’utilisateur peut :

- consulter les quantités encore retournables ;
- choisir une quantité par ligne ;
- choisir l’emplacement de réintégration ;
- conserver le lot béton expédié ;
- enregistrer un commentaire ;
- effectuer plusieurs retours partiels.

## Contrôle des quantités

Pour chaque ligne :

```text
Retournable =
Somme des sorties non annulées
− Somme des retours non annulés
```

Il est impossible de retourner plus que la quantité encore retournable.

## Traçabilité

La migration `0021` ajoute sur les mouvements :

```text
preparation_id
ligne_preparation_id
```

Les mouvements d’expédition du Lot D sont désormais liés à la préparation et
à sa ligne. Les mouvements de retour reprennent ces mêmes liens.

## Atomicité

Toutes les lignes d’un retour sont traitées dans une seule transaction.

Si une ligne est invalide :

- aucun stock n’est réintégré ;
- aucun mouvement de retour n’est conservé.

## Stock

Un retour crée un mouvement `RETOUR` :

- augmentation du stock physique article ;
- augmentation du stock physique du lot béton ;
- aucune réservation créée.

## Migration

```text
0021
```

Prérequis :

```text
0020
```

## Installation

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
0021 (head)
Application startup complete
Ready
```

## Recette

1. Expédier une préparation.
2. Relever les stocks après expédition.
3. Cliquer sur `Enregistrer un retour`.
4. Retourner partiellement une ligne.
5. Vérifier :
   - mouvement `RETOUR` créé ;
   - stock article augmenté ;
   - stock lot augmenté ;
   - affaire et préparation liées.
6. Ouvrir à nouveau le retour :
   - la quantité retournable doit avoir diminué.
7. Tenter de dépasser la quantité restante :
   - refus attendu ;
   - aucune modification partielle.
8. Retourner le reliquat :
   - la ligne ne doit plus être proposée.

## Git après validation

```powershell
git status
git add .
git commit -m "feat: add traceable site returns"
git push
```
