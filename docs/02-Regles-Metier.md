# Règles métier — COREF Logistique

## Référentiel familles

- Les familles et sous-familles sont administrables.
- Une famille ou sous-famille utilisée n’est jamais supprimée physiquement.
- L’archivage utilise le champ `actif`.
- Le code d’une famille est unique.
- Le code d’une sous-famille est unique dans sa famille.
- La famille `Moules` constitue un référentiel métier distinct.
- Les bétons sont les seuls articles soumis aux exigences renforcées de lot,
  fabrication, péremption, certificat fournisseur, FDS et traçabilité à l’affaire.

## Stocks

- Une ligne de stock associe un article à un emplacement unique.
- La quantité disponible est égale à la quantité physique moins la quantité réservée.
- Une quantité ne peut jamais être négative.
- La quantité réservée ne peut pas dépasser la quantité physique.
- La saisie directe du stock est provisoirement autorisée pour l’initialisation.
- Après mise en place du module Mouvements, toute variation devra être historisée.
- Le stock minimum, le seuil d’alerte et le stock maximum sont portés par l’article.
- Une rupture correspond à une quantité disponible inférieure ou égale à zéro.
