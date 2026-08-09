# Lot 13 — Inventaires

## Fonctionnalités

- campagne d’inventaire par emplacement ;
- génération automatique `INV-000001` ;
- photographie des quantités théoriques au démarrage ;
- comptage par article et, pour les bétons, par lot ;
- calcul automatique des écarts ;
- validation avec création de mouvements d’ajustement ;
- traçabilité complète dans l’historique des mouvements.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du dépôt, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0009 -> 0010
```

## Test

1. Ouvrir `http://localhost:3000/inventaires`.
2. Créer un inventaire du `Magasin Principal`.
3. Saisir les quantités comptées.
4. Créer volontairement un écart positif ou négatif.
5. Valider.
6. Vérifier les nouveaux mouvements d’ajustement.
7. Vérifier que le stock correspond désormais au comptage.

## Git

```powershell
git status
git add .
git commit -m "feat: add inventory campaigns"
git push
```
