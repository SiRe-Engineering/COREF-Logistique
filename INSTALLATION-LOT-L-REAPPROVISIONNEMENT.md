# Lot L — Réapprovisionnement

## Fonctions

Nouvel onglet `Réapprovisionnement`.

### Suggestions automatiques

Un article apparaît lorsque :

```text
disponible <= 0
```

ou :

```text
disponible <= max(stock minimum, seuil d'alerte)
```

Quantité proposée :

```text
si stock maximum > 0 :
    stock maximum - disponible
sinon :
    stock minimum - disponible
```

Une suggestion ne crée pas automatiquement une commande : l'utilisateur
clique `Créer le besoin`.

### Cycle

```text
A_TRAITER → VALIDE → COMMANDE → RECU
                         ↘
                          ANNULE
```

Un seul besoin ouvert par article est autorisé.

### Réception

La réception demande :

- quantité ;
- prix unitaire HT ;
- emplacement destination ;
- lot pour le béton ;
- commentaire.

Elle crée un vrai mouvement `ENTREE`, lié au besoin, et utilise le moteur de
stock existant. Le CUMP et le dernier prix d'achat sont donc recalculés par la
logique déjà validée.

Les réceptions partielles sont supportées.

## Migration

```text
0027
```

Elle crée `besoins_reapprovisionnement` et rattache les mouvements d'entrée au
besoin source.

## Installation

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

Puis :

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Attendu :

```text
0027 (head)
```

Puis `Ctrl + F5`.

## Recette

1. Renseigner mini / maxi / seuil sur un article.
2. Vérifier sa suggestion.
3. Créer le besoin.
4. Renseigner fournisseur, prix et référence commande.
5. Passer `VALIDE`, puis `COMMANDE`.
6. Faire une réception partielle.
7. Vérifier Stocks + Mouvements + CUMP.
8. Réceptionner le solde.
9. Vérifier le statut `RECU`.
10. Pour un article Béton, vérifier que le lot est obligatoire.

## Git

```powershell
git status
git add .
git commit -m "feat: add replenishment workflow"
git push
```
