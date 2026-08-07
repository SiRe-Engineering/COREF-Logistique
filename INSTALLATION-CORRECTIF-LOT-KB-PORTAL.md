# Correctif Lot K-B — Modale d’édition au premier plan

Le `Drawer` crée son propre contexte d’empilement. Une simple augmentation du
`z-index` de la modale n’est donc pas suffisante.

Ce correctif rend la fenêtre `Modifier l’article` directement dans
`document.body` avec `createPortal()`.

## Installation

Le fichier `page.tsx` remplace :

```text
frontend/app/articles/page.tsx
```

Le contenu de :

```text
frontend/app/globals.css
```

doit être ajouté à la fin de ton `globals.css` existant, pas remplacer tout le
fichier.

Puis :

```powershell
docker compose up --build -d frontend
```

Et :

```text
Ctrl + F5
```

## Vérification

1. Articles.
2. Ouvrir une fiche article.
3. Cliquer `Modifier l’article`.
4. La fenêtre d’édition doit apparaître au-dessus de la fiche détaillée.
5. Cliquer hors de la fenêtre doit la fermer sans fermer le Drawer.
