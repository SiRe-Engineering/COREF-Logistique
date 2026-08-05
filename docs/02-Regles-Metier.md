# Règles métier — COREF Logistique

## Référentiels

- Les familles et sous-familles sont administrables.
- Une entité utilisée n’est jamais supprimée physiquement.
- L’archivage utilise le champ `actif`.

## Stocks et mouvements

- Une ligne de stock associe un article à un emplacement unique.
- La quantité disponible est égale à la quantité physique moins la quantité réservée.
- Un mouvement validé est immuable.
- Une erreur est corrigée par un mouvement inverse ou un ajustement.
- Le mouvement et la mise à jour du stock sont enregistrés dans la même transaction.

## Lots béton

- Tout mouvement d’un article Béton exige un lot.
- Le stock agrégé et le stock par lot sont mis à jour dans la même transaction.
- Une sortie ne peut dépasser le disponible du lot.
- Les lots sont proposés par péremption croissante selon le FEFO.

## Affaires

- Une affaire peut représenter un chantier ou une affaire atelier.
- Une affaire reçoit une référence interne automatique `AFF-000001`.
- Le code externe COREF ou ERP est facultatif mais unique lorsqu’il est renseigné.
- Une sortie doit être rattachée à une affaire active ou être explicitement déclarée libre.
- Une affaire terminée ou annulée n’accepte plus de nouvelles sorties.
- Le chargé d’affaires et la zone d’intervention sont repris automatiquement sur le mouvement.
- Le véhicule peut être renseigné au moment de la sortie.
- La relation entre mouvement, affaire, article et lot permet la traçabilité complète des bétons jusqu’au chantier.
