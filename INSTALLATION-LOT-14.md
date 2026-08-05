# Lot 14 — Préparations de chantier

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du projet, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0010 -> 0011
```

## Test recommandé

1. Ouvrir `http://localhost:3000/preparations`.
2. Créer une préparation pour l’affaire `20260001`.
3. Ajouter le béton LB85, son lot et le Magasin Principal.
4. Demander une quantité inférieure au disponible.
5. Valider la préparation.
6. Démarrer la préparation.
7. Saisir la quantité préparée.
8. Marquer la préparation prête.
9. Expédier.
10. Vérifier :
    - la préparation au statut `EXPEDIEE` ;
    - la création d’une sortie dans Mouvements ;
    - la diminution du stock ;
    - la présence de l’affaire et du lot sur le mouvement.

## Git

```powershell
git status
git add .
git commit -m "feat: add job preparation workflow"
git push
```
