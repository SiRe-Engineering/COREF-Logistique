# Lot K — Centre d’alertes

## Différence entre dashboard et alertes

Le dashboard représente l’état instantané.

Le centre d’alertes apporte :

- persistance ;
- date de première détection ;
- acquittement ;
- résolution automatique ;
- réapparition ;
- historique.

## Synchronisation

Une synchronisation recalcule les signaux métier puis compare leurs clés avec
les alertes persistées.

Exemples :

```text
STOCK:RUPTURE:42
STOCK:SEUIL:42
LOT:PEREMPTION:17
PREPARATION:RETARD:8
PREPARATION:BLOQUEE:8
INVENTAIRE:ANCIEN:4
```

La clé garantit qu’une anomalie n’est pas dupliquée à chaque lecture.

## Philosophie

L’utilisateur peut acquitter une alerte, mais pas la déclarer arbitrairement
résolue. La résolution appartient à la donnée métier.
