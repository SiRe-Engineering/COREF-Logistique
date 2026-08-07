# Lot I-B — Analyse de valorisation

## Nouvel onglet

```text
Valorisation
```

Route :

```text
/valorisation
```

## Contenu

### KPI

- valeur physique du stock ;
- valeur réservée ;
- valeur disponible ;
- variation par rapport au snapshot mensuel précédent.

### Évolution mensuelle

Le graphique affiche jusqu’à 24 mois :

- valeur physique ;
- valeur réservée ;
- valeur disponible.

Filtres :

```text
6 mois
12 mois
24 mois
```

### Répartition par famille

La valeur actuelle est agrégée par famille à partir de :

```text
quantité × CUMP article
```

Le module présente :

- graphique en barres horizontales ;
- valeur physique ;
- valeur réservée ;
- valeur disponible ;
- part de chaque famille dans la valeur physique totale.

## Historisation automatique

La table :

```text
snapshots_valorisation_stock
```

contient une ligne par mois.

Le snapshot du mois courant est mis à jour automatiquement lors :

- d’un mouvement de stock ;
- d’une annulation de mouvement ;
- d’une modification manuelle du CUMP ;
- d’une modification directe d’un stock ;
- d’une remise à zéro technique ;
- de l’ouverture de l’onglet Valorisation.

À la fin du mois, la dernière valeur connue du mois reste figée.

Le mois suivant crée automatiquement une nouvelle ligne.

## Important

L’historique démarre à l’installation du Lot I-B. Le logiciel ne reconstitue
pas artificiellement les mois précédents, car les CUMP historiques n’étaient
pas enregistrés avant le Lot I.

## Migration

```text
0025
```

Prérequis :

```text
0024
```

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

Résultat attendu :

```text
0025 (head)
```

Faire ensuite :

```text
Ctrl + F5
```

## Recette

1. Ouvrir `Valorisation`.
2. Vérifier la cohérence avec la valeur du dashboard.
3. Vérifier la répartition par famille.
4. Modifier un CUMP et recharger : le mois courant doit évoluer.
5. Créer une entrée avec prix d’achat : le snapshot doit évoluer.
6. Créer une sortie : le snapshot doit évoluer.
7. Vérifier qu’il n’existe qu’une ligne de snapshot pour le mois courant.
8. Vérifier les vues 6 / 12 / 24 mois.

## Git

```powershell
git status
git add .
git commit -m "feat: add stock valuation analytics"
git push
```
