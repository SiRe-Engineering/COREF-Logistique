# Règles métier — COREF Logistique

## Stocks, mouvements et affaires

- Une sortie doit être rattachée à une affaire active ou être déclarée libre.
- Les mouvements sont immuables.
- Les mouvements de béton exigent un lot.
- Le stock et le stock par lot sont mis à jour dans la même transaction.

## Matériels

- Chaque matériel reçoit un numéro d’inventaire automatique `MAT-000001`.
- Un numéro de série, lorsqu’il est renseigné, est unique.
- Les états disponibles sont : Disponible, En chantier, En maintenance,
  Hors service et Perdu.
- Un matériel en chantier doit obligatoirement être affecté à une affaire active.
- Une affaire terminée ou annulée ne peut pas recevoir de matériel.
- La prochaine date de contrôle ne peut pas précéder le dernier contrôle.
- Les échéances sous trente jours sont considérées comme des alertes.
- Le matériel peut être localisé dans un emplacement COREF.
- La modification de l’état et de l’affectation est historisée uniquement à
  partir du futur module de mouvements de matériel.
