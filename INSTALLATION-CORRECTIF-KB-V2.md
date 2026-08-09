# Correctif K-B V2 — Fenêtre Modifier l’article

Ce correctif ne modifie que :

```text
frontend/app/articles/page.tsx
```

Aucun fichier CSS global ne doit être remplacé.

## Cause

Le Drawer utilise :

```text
z-index: 120
```

La classe globale `modal-backdrop` utilise :

```text
z-index: 100
```

Le React Portal sort bien la modale du Drawer, mais son `z-index` restait donc
inférieur à celui du Drawer.

## Correctif

Le backdrop d’édition reçoit directement :

```text
z-index: 10000
```

et la carte :

```text
z-index: 10001
```

## Installation

Remplacer uniquement :

```text
frontend/app/articles/page.tsx
```

Puis :

```powershell
docker compose up --build -d frontend
```

et :

```text
Ctrl + F5
```
