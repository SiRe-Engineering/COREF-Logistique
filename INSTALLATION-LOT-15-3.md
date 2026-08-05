# Lot 15.3 — Séparation SiRe Engineering / COREF

## Comptes créés

### Administrateur technique

```text
Nom affiché : SiRe Engineering
E-mail : contact@sire-engineering.fr
Mot de passe temporaire : Sire-2026!
Rôle : Administrateur technique
Entreprise : SiRe Engineering
```

Ce compte est distinct de toute opération métier COREF.

### Administrateur métier COREF

```text
Nom : Simon Goubet
E-mail : simon.goubet@coref.fr
Mot de passe temporaire : Coref-2026!
Rôle : Administrateur COREF
Entreprise : COREF
Fonction : Directeur Général Adjoint
```

## Droits

L'administrateur technique peut voir et gérer tous les comptes.

L'administrateur COREF :

- gère les utilisateurs métier COREF ;
- ne voit pas les comptes techniques SiRe Engineering ;
- ne peut pas créer ni modifier un administrateur technique.

## Installation

Depuis la racine du projet :

```powershell
docker compose down
```

Copier tous les fichiers du lot, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`.

Migration attendue :

```text
Running upgrade 0015 -> 0016
```

## Tests de connexion

Compte technique :

```text
contact@sire-engineering.fr
Sire-2026!
```

Compte métier :

```text
simon.goubet@coref.fr
Coref-2026!
```

Après connexion avec Simon Goubet, la page Utilisateurs ne doit afficher que
les comptes métier COREF.

Après connexion avec SiRe Engineering, elle peut afficher les comptes
techniques et métier.

## Important

Les mots de passe indiqués sont temporaires. Le prochain correctif pourra
ajouter une page permettant à chaque utilisateur de modifier son propre mot
de passe.

## Git

```powershell
git status
git add .
git commit -m "feat: separate technical and COREF user accounts"
git push
```
