# Lot 15 — Utilisateurs, rôles et connexion

## Fonctionnalités

- écran de connexion ;
- sessions de douze heures ;
- mots de passe hachés avec PBKDF2-SHA256 ;
- gestion des utilisateurs ;
- six rôles initiaux ;
- notifications rattachées automatiquement au compte connecté ;
- suppression du sélecteur manuel d'utilisateur ;
- menu utilisateur avec déconnexion ;
- accès à l'administration réservé aux administrateurs.

## Rôles

- Administrateur
- Responsable logistique
- Responsable production
- Chargé d'affaires
- Utilisateur standard
- Consultation

Ce lot pose le socle d'authentification. Les autorisations détaillées sur chaque
module et le workflow de validation seront ajoutés au lot suivant.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du projet, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0013 -> 0014
```

## Première connexion

```text
E-mail : admin@coref.local
Mot de passe : Coref-2026!
```

Changer ensuite ce mot de passe en créant un nouvel administrateur ou via
l'API PATCH temporaire.

## Création des utilisateurs

Ouvrir :

```text
http://localhost:3000/administration/utilisateurs
```

Créer les comptes avec un nom complet identique à celui utilisé comme
demandeur ou préparateur. Les notifications historiques correspondantes
apparaîtront automatiquement.

## Important

Le package ajoute `email-validator` dans `backend/requirements.txt`.
Le backend doit donc être reconstruit avec `--build`.

## Git

```powershell
git status
git add .
git commit -m "feat: add users roles and authentication"
git push
```
