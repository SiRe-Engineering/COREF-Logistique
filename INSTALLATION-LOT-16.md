# Lot 16 — Validation des sorties selon les rôles

## Règles

Un utilisateur standard crée une demande `DS-000001`. Le stock ne bouge pas
tant qu'elle n'est pas approuvée.

Peuvent approuver ou refuser :

- Responsable logistique
- Responsable production
- Chargé d'affaires
- Administrateur COREF
- Administrateur technique

Ces rôles peuvent aussi enregistrer directement leurs propres sorties.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0016 -> 0017
```

## Test

1. Créer un utilisateur standard et un responsable logistique.
2. Se connecter avec l'utilisateur standard.
3. Créer une demande dans `Demandes de sortie`.
4. Vérifier que le stock n'a pas diminué.
5. Se connecter avec le responsable logistique.
6. Approuver la demande.
7. Vérifier le mouvement, le stock et la notification du demandeur.
8. Refaire le test avec un refus motivé.

## Git

```powershell
git status
git add .
git commit -m "feat: add role based stock issue approval"
git push
```
