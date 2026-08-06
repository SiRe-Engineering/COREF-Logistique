# Lot 18.3A — Proposition et décision de remplacement

## Périmètre strict

Ce lot ajoute uniquement :

- la proposition d’un article de remplacement ;
- l’emplacement proposé ;
- le lot proposé lorsque l’article est un béton ;
- la quantité proposée ;
- un commentaire obligatoire ;
- l’acceptation ou le refus ;
- l’identité du proposant et du décideur ;
- les notifications associées.

## Important

Ce sous-lot ne déplace encore aucune réservation et ne modifie aucun stock.

Le déplacement de réservation sera ajouté dans le lot 18.3B, uniquement
après validation et commit de ce sous-lot.

## Installation

Prérequis :

```text
Git : dernier commit validé du lot 18.2
Alembic : 0018
```

Copier l’archive à la racine, puis :

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

## Contrôles techniques

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Résultats attendus :

```text
0019 (head)
Application startup complete
{"status":"ok","database":"connected","version":"1.0.0"}
```

## Checklist fonctionnelle

- [ ] Ouvrir une préparation en cours.
- [ ] Déclarer une ligne indisponible.
- [ ] Vérifier l’apparition du bouton `↻`.
- [ ] Proposer un autre article.
- [ ] Choisir un emplacement.
- [ ] Pour un béton, choisir un lot.
- [ ] Saisir une quantité et un commentaire.
- [ ] Vérifier le statut `Remplacement proposé`.
- [ ] Vérifier la notification du demandeur.
- [ ] Accepter avec le demandeur ou un responsable autorisé.
- [ ] Vérifier le statut `Remplacement accepté`.
- [ ] Vérifier la notification du préparateur.
- [ ] Refaire le scénario avec un refus.
- [ ] Vérifier qu’un motif est obligatoire pour le refus.
- [ ] Vérifier que les stocks et réservations n’ont pas changé.

## Commit après validation uniquement

```powershell
git status
git add .
git commit -m "feat: add replacement proposal and decision workflow"
git push
```
