# Lot 22 — Remise à zéro technique des stocks

## Objectif

Permettre à l’administrateur technique SiRe Engineering de remettre un stock
complètement à plat lorsqu’un stock article, ses lots et ses réservations
divergent.

## Action

Dans l’onglet Stocks, le bouton `Remettre à zéro` agit sur l’article et
l’emplacement sélectionnés.

Il met à zéro :

```text
Stock.quantite_physique
Stock.quantite_reservee
Tous les StockLot.quantite_physique associés
Tous les StockLot.quantite_reservee associés
```

Il libère également les `ReservationStock` actives correspondant au même
article et au même emplacement.

## Éléments conservés

- les articles ;
- les lots et leur traçabilité ;
- les préparations ;
- l’historique des mouvements ;
- les réservations libérées dans l’historique.

## Sécurité

Action exclusivement réservée à :

```text
ADMINISTRATEUR_TECHNIQUE
```

Aucune justification n’est demandée. Une confirmation détaillée est affichée.

## Installation

Aucune migration supplémentaire.

Copier l’archive à la racine puis :

```powershell
docker compose up --build -d backend frontend
```

## Contrôles

```powershell
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

## Test conseillé

1. Relever un stock béton divergent.
2. Cliquer sur `Remettre à zéro`.
3. Vérifier dans Stocks :
   - physique = 0 ;
   - réservé = 0 ;
   - disponible = 0.
4. Vérifier les lots du même article/emplacement :
   - physique = 0 ;
   - réservé = 0.
5. Vérifier que les réservations actives sont libérées.
6. Ressaisir ensuite les quantités réelles lot par lot.

## Git

```powershell
git status
git add .
git commit -m "feat: add technical stock reset to zero"
git push
```
