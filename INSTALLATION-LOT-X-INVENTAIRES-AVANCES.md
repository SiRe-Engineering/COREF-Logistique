# Lot X — Inventaires avancés & écarts de stock

Migration : `0038` après `0037`.

## Fonctions
- campagnes d'inventaire `INV-000001` ;
- photographie du stock théorique au lancement ;
- comptage physique par article et emplacement ;
- calcul automatique de l'écart quantité ;
- valorisation de l'écart ;
- justification obligatoire lorsqu'un écart existe ;
- validation globale uniquement lorsque toutes les lignes sont comptées ;
- régularisation du stock uniquement à la validation ;
- création de mouvements `AJUSTEMENT_INVENTAIRE` pour conserver la traçabilité.

## Sécurité métier
Le comptage ne modifie jamais directement le stock.
La régularisation n'est effectuée qu'au moment de la validation finale de la campagne.

## Installation
Copier le contenu à la racine du projet.

Il faut ensuite raccorder le nouveau modèle et le nouveau router aux fichiers
`backend/app/models/__init__.py`, `backend/app/api/__init__.py` et `backend/app/main.py`
selon les imports déjà utilisés dans le projet, puis ajouter l'accès
`/inventaire/avance` dans le module Inventaire existant.

Ensuite :

```powershell
docker compose down
docker compose up --build -d
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
```

Attendu :

```text
0038 (head)
```

## Recette
1. Créer une campagne.
2. Vérifier que les quantités théoriques correspondent au stock avant comptage.
3. Saisir une ligne sans écart.
4. Saisir une ligne avec écart : une justification doit être exigée.
5. Vérifier le calcul de l'écart en valeur.
6. Essayer de valider avant d'avoir tout compté : validation refusée.
7. Compléter le comptage puis valider.
8. Vérifier le stock régularisé.
9. Vérifier la présence des mouvements `AJUSTEMENT_INVENTAIRE`.
