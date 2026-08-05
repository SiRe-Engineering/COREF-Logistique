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
- Le stock minimum, le seuil d’alerte et le stock maximum sont portés par l’article.
- Une rupture correspond à une quantité disponible inférieure ou égale à zéro.

## Mouvements

- Un mouvement validé est immuable et ne doit pas être supprimé.
- Une erreur est corrigée par un mouvement inverse ou un ajustement.
- Le mouvement et la mise à jour du stock sont enregistrés dans la même transaction.
- Chaque mouvement reçoit une référence automatique `MVT-000001`.

## Lots béton

- Un lot renforcé ne peut être créé que pour un article de famille `Béton`.
- Le numéro de lot fournisseur est unique pour un même article.
- La date de péremption ne peut pas précéder la date de fabrication.
- Tout mouvement d’un article Béton exige un lot.
- Le lot sélectionné doit appartenir à l’article du mouvement.
- Le stock agrégé Article/Emplacement et le stock Lot/Emplacement sont mis à
  jour dans la même transaction.
- Une sortie ou un transfert ne peut dépasser le disponible du lot.
- Les lots sont proposés par péremption croissante afin d’appliquer le FEFO.
- Les stocks de béton existants sont repris automatiquement dans un lot
  technique `LOT-INITIAL` lors de la migration `0007`.
