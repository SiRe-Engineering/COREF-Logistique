# COREF Logistique V2.0.1 — Fiche Préparation

## Évolutions

- fiche en mode `workspace` à environ 82 % de l’écran ;
- informations principales visibles immédiatement ;
- KPI et progression globale ;
- tableau dense des lignes ;
- saisie directe des quantités préparées ;
- quantités manquantes et anomalies visibles ;
- barre d’actions persistante ;
- structure prête pour les remplacements d’articles.

## Prérequis

- V2.0.0 — Fondation UX ;
- lot 18.1 — Statuts des lignes de préparation.

## Installation

Remplacer :

```text
frontend/app/preparations/page.tsx
frontend/app/preparations/page.module.css
```

Puis :

```powershell
docker compose restart frontend
```

Si nécessaire :

```powershell
docker compose up --build -d frontend
```

Aucune migration de base de données n’est nécessaire.

## Contrôle

1. Ouvrir une préparation.
2. Vérifier que la fiche occupe environ 80 % de l’écran.
3. Vérifier les KPI et la barre de progression.
4. Vérifier le tableau des lignes.
5. Démarrer une préparation et saisir les quantités.
6. Tester l’édition et la suppression des lignes.
7. Vérifier que la barre d’actions reste accessible.

## Git

```powershell
git status
git add frontend/app/preparations INSTALLATION-V2-0-1.md
git commit -m "refactor: redesign preparation workspace"
git push
```
