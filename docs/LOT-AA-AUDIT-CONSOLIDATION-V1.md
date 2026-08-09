# Lot AA — Consolidation V1

Audit réalisé sur l'archive complète transmise après validation du Lot Z.

## Corrections incluses

1. Nettoyage de `main.py` : suppression des raccordements ajoutés en fin de fichier par les lots X/Y.
2. Centralisation de tous les routeurs dans `app.api`.
3. Protection globale des API métier par `utilisateur_courant`.
4. Conservation volontaire de `/api/health` et `/api/auth/*` comme routes publiques nécessaires au fonctionnement.
5. Export explicite des modèles `CampagneInventaireAvance` et `LigneInventaireAvance`.
6. Suppression du menu V1 des entrées non fonctionnelles `Familles`, `Moules`, `Véhicules` et `Système`.

## Non modifié volontairement dans AA.1

- aucune table PostgreSQL ;
- aucune migration Alembic ;
- aucun workflow stock ;
- aucun statut métier ;
- aucun historique existant ;
- aucune suppression du système d'inventaire historique.

La suppression des mots de passe bootstrap historiques et la configuration Docker de production seront traitées dans la phase de préparation au déploiement, afin de ne pas bloquer l'environnement local actuellement validé.

## Point Git important

L'archive auditée contient de nombreux fichiers P→Z encore non suivis. Après validation fonctionnelle de AA, créer un point de restauration Git complet avant toute nouvelle évolution.
