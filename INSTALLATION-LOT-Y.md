# Lot Y — Centre d'alertes logistiques

## Principe
Le Lot Y ne crée aucune nouvelle table. Il agrège les informations déjà présentes
dans COREF Logistique et évite ainsi de dupliquer les données métier.

Le centre remonte notamment :
- stock au minimum ou sous le minimum ;
- commandes fournisseurs en retard ;
- documents matériel expirés ou à échéance sous 30 jours ;
- maintenance / contrôles matériel en retard ou à prévoir ;
- préparations en retard ;
- inventaires avancés encore en cours.

Priorités :
- `CRITIQUE`
- `ATTENTION`
- `INFO`

Chaque alerte est cliquable et renvoie vers son module métier.

## Installation
Extraire le ZIP à la racine du projet puis :

```powershell
powershell -ExecutionPolicy Bypass -File .\RACCORDER-LOT-Y.ps1
```

Aucune migration Alembic.

## Accès
```text
http://localhost:3000/alertes
```

## Recette
1. Vérifier qu'un article exactement au stock mini apparaît bien en `ATTENTION`.
2. Vérifier qu'un article sous le mini apparaît en `CRITIQUE`.
3. Vérifier une commande fournisseur en retard.
4. Vérifier un document matériel à échéance / expiré si disponible.
5. Cliquer une alerte et vérifier l'ouverture du bon module.
