# Lot 06 — Design system et panneau Article

## Installation

```powershell
docker compose stop frontend
```

Copier les fichiers du lot à la racine du dépôt, puis :

```powershell
docker compose up --build -d frontend
docker compose logs frontend --tail=100
```

Le changement de `package.json` installe `lucide-react`.

## Vérifications

- menu actif ;
- icônes Lucide ;
- bouton `Nouvel article` secondaire ;
- tri des colonnes ;
- clic sur une ligne et ouverture du panneau latéral ;
- badges de famille ;
- notifications après création ou archivage.

## Git

```powershell
git add .
git commit -m "feat: add frontend design system and article drawer"
git push
```
