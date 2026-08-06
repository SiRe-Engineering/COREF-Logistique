# Correctif fenêtre de retour — React Portal

Ce correctif rend la fenêtre de retour directement dans `document.body`
avec `createPortal()`.

Il contourne totalement le contexte d’empilement du `Drawer`.

## Installation

Copier le contenu de l’archive à la racine du projet, puis :

```powershell
docker compose up --build -d frontend
```

Faire ensuite un rechargement forcé du navigateur :

```text
Ctrl + F5
```

## Vérification

1. Ouvrir une préparation expédiée.
2. Cliquer sur `Enregistrer un retour`.
3. La fenêtre doit apparaître au-dessus du Drawer.
4. Saisir une quantité et un emplacement.
5. Cliquer sur `Réintégrer en stock`.
6. Vérifier le POST dans Network.
