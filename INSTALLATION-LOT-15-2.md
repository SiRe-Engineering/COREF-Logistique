# Lot 15.2 — Correctif de l'adresse administrateur

## Cause

`admin@coref.local` est refusé par `EmailStr`, car le suffixe `.local`
est réservé et n'est pas considéré comme une adresse e-mail valide.

## Nouveau compte initial

```text
E-mail : admin@coref.fr
Mot de passe : Coref-2026!
```

## Installation

Depuis la racine du projet :

```powershell
docker compose down
```

Copier tous les fichiers du lot en acceptant les remplacements, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0014 -> 0015
```

Cette migration remplace automatiquement dans la base :

```text
admin@coref.local
```

par :

```text
admin@coref.fr
```

## Test

Ouvrir :

```text
http://localhost:3000
```

Puis se connecter avec :

```text
E-mail : admin@coref.fr
Mot de passe : Coref-2026!
```

## Git

```powershell
git add .
git commit -m "fix: use valid administrator email"
git push
```
