# Lot 05 — Interface Articles

Ce lot remplace l’interface de démonstration par une première application
métier responsive.

## Installation

Arrêter uniquement le frontend :

```powershell
docker compose stop frontend
```

Copier le contenu du lot à la racine du dépôt en acceptant le remplacement
des fichiers, puis reconstruire :

```powershell
docker compose up --build -d frontend
```

Le backend et PostgreSQL ne sont pas modifiés.

## Vérifications

- Tableau de bord : http://localhost:3000
- Articles : http://localhost:3000/articles

Tester :

1. l’ouverture de la page Articles ;
2. la recherche ;
3. le filtre par famille ;
4. le bouton `Nouvel article` ;
5. le chargement dynamique des sous-familles ;
6. la création sans référence manuelle ;
7. l’affichage de la référence `ART-XXXXXX` retournée par l’API ;
8. l’archivage d’un article.

## Git

```powershell
git status
git add .
git commit -m "feat: add articles management interface"
git push
```
