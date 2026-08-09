# Lot J — Documents & identification terrain

## Choix d’architecture

Les documents restent des vues HTML optimisées pour l’impression.

Avantages :

- aperçu immédiat ;
- impression directe ;
- export PDF natif du navigateur ;
- aucune bibliothèque PDF serveur ;
- maintenance simple.

## Identification QR

Le contenu du QR n’introduit pas de nouvel identifiant.

```text
Article -> référence article
Lot béton -> référence interne du lot
```

Le résultat est donc immédiatement compatible avec `/api/magasin/scan/...`.

## Formats

```text
Documents : A4 paysage
Étiquettes : 90 × 50 mm
```

Le CSS `@page` permet au navigateur de proposer le bon format d’impression.
