# Lot 16.1 — Édition et suppression des utilisateurs

## Règles de sécurité

Seuls les rôles suivants peuvent accéder à la gestion des utilisateurs :

- Administrateur technique ;
- Administrateur COREF.

Un administrateur COREF peut uniquement gérer les comptes métier de COREF.

Un administrateur technique peut gérer les comptes techniques et métier.

Un administrateur ne peut pas modifier ou supprimer son propre compte depuis
cette page afin d'éviter de perdre accidentellement l'accès à l'application.

## Édition

Le bouton crayon permet de modifier :

- le prénom et le nom ;
- l'adresse e-mail ;
- l'entreprise, pour l'administrateur technique ;
- la fonction ;
- le rôle ;
- le mot de passe ;
- le statut actif ou inactif.

Lors d'une édition, laisser le champ de mot de passe vide conserve le mot de
passe existant.

## Suppression sécurisée

Le bouton corbeille ne détruit pas physiquement l'enregistrement.

Il :

1. désactive immédiatement le compte ;
2. révoque toutes ses sessions ouvertes ;
3. empêche toute nouvelle connexion ;
4. conserve son nom dans l'historique des mouvements, validations et demandes.

Le compte apparaît ensuite avec le statut `Supprimé`. Il peut être réactivé
par un administrateur avec le bouton Modifier.

## Installation

Remplacer :

```text
backend/app/api/utilisateurs.py
frontend/app/administration/utilisateurs/page.tsx
```

Ajouter :

```text
frontend/app/administration/utilisateurs/page.module.css
```

Puis :

```powershell
docker compose restart backend frontend
```

Si le frontend ne recharge pas correctement :

```powershell
docker compose up --build -d backend frontend
```

Aucune migration de base de données n'est nécessaire.

## Tests

1. Se connecter avec Simon Goubet ou SiRe Engineering.
2. Modifier le rôle ou la fonction de Maxence WEINGAND.
3. Vérifier que la modification apparaît dans la liste.
4. Supprimer Maxence WEINGAND.
5. Vérifier :
   - statut `Supprimé` ;
   - connexion impossible avec ce compte ;
   - historique métier conservé.
6. Modifier à nouveau le compte et le remettre au statut `Actif`.
7. Vérifier qu'aucun bouton d'action n'apparaît sur le compte actuellement
   connecté.

## Git

```powershell
git status
git add backend/app/api/utilisateurs.py frontend/app/administration/utilisateurs
git commit -m "feat: allow administrators to manage user accounts"
git push
```
