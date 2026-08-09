# Correctif Lot F — Nommage automatique des inventaires

## Règle appliquée

Le champ `Nom` libre est supprimé.

Le backend génère automatiquement :

```text
2026-08-06 - Emplacement - Magasin Principal
2026-08-06 - Emplacement - Mezzanine Isolants
2026-08-06 - Famille - Isolants
2026-08-06 - Famille - Béton
2026-08-06 - Général
```

Si un inventaire identique existe déjà le même jour :

```text
2026-08-06 - Emplacement - Magasin Principal (2)
2026-08-06 - Emplacement - Magasin Principal (3)
```

## Interface

La fenêtre de création affiche un aperçu du nom calculé.

L’utilisateur choisit uniquement :

- le type ;
- l’emplacement ou la famille ;
- le commentaire éventuel.

## Migration

Aucune migration supplémentaire.

## Installation

```powershell
docker compose up --build -d backend frontend
```

Puis rechargement forcé :

```text
Ctrl + F5
```

## Vérification

1. Créer un inventaire par emplacement.
2. Vérifier le nom automatique.
3. Créer un inventaire par famille.
4. Vérifier le nom automatique.
5. Créer un inventaire général.
6. Recréer le même inventaire le même jour.
7. Vérifier le suffixe `(2)`.

## Git

```powershell
git status
git add .
git commit -m "fix: generate inventory names automatically"
git push
```
