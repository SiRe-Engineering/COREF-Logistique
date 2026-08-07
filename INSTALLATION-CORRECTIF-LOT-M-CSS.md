# Correctif Lot M — CSS Modules

Le build Next.js échouait car `page.module.css` contenait des sélecteurs globaux
comme :

```css
table
th
td
```

Dans un CSS Module, chaque sélecteur doit contenir au moins une classe ou un
identifiant local.

Le correctif remplace donc notamment :

```css
table
```

par :

```css
.panel table
```

et :

```css
th,
td
```

par :

```css
.panel th,
.panel td
```

## Installation

Remplacer uniquement :

```text
frontend/app/achats/page.module.css
```

Puis :

```powershell
docker compose up --build -d frontend
```

Vérifier :

```powershell
docker compose logs frontend --tail=100
```

Puis faire :

```text
Ctrl + F5
```

Aucune migration ni modification backend.
