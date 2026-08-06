# Lot F — Inventaires V1

## Fonctions

- inventaire par emplacement ;
- inventaire général ;
- inventaire par famille ;
- photographie du stock théorique au démarrage ;
- comptage par article, emplacement et lot ;
- saisie d’un commentaire ;
- calcul automatique de l’écart ;
- validation réservée aux responsables ;
- mouvements d’ajustement positifs ou négatifs ;
- validation atomique ;
- verrouillage après validation ;
- traçabilité des mouvements vers l’inventaire.

## Source de vérité

Avant validation, le stock n’est jamais modifié.

À la validation :

```text
Écart positif
→ AJUSTEMENT_POSITIF

Écart négatif
→ AJUSTEMENT_NEGATIF
```

## Réservations

Un ajustement négatif ne peut pas rendre le stock physique inférieur au stock
réservé. La validation est refusée et toute l’opération est annulée.

## Migration

```text
0023
```

Prérequis :

```text
0022
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
0023 (head)
```

## Recette

1. Créer un inventaire par emplacement.
2. Vérifier la reprise des articles et des lots.
3. Saisir les quantités comptées.
4. Vérifier les écarts avant validation.
5. Vérifier que le stock n’a pas encore changé.
6. Valider avec un responsable autorisé.
7. Vérifier :
   - stock physique régularisé ;
   - mouvements d’ajustement créés ;
   - inventaire lié aux mouvements ;
   - inventaire verrouillé ;
   - valideur et date enregistrés.
8. Tester un ajustement négatif sous le stock réservé :
   - refus attendu ;
   - aucun mouvement partiel ;
   - inventaire toujours en cours.
9. Tester un inventaire général.
10. Tester un inventaire par famille.

## Git

```powershell
git status
git add .
git commit -m "feat: add validated inventory campaigns"
git push
```
