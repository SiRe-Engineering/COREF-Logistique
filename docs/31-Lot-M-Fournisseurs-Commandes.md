# Lot M — Fournisseurs & commandes d'achat

Le Lot L reste le moteur du besoin. Le Lot M transforme ces besoins en commandes fournisseur multi-lignes.

La réception passe toujours par `executer_mouvement()`. Il n'existe donc pas de seconde logique de stock : CUMP, dernier prix d'achat, snapshots de valorisation et lots béton restent gouvernés par le moteur déjà validé.

La table `articles_fournisseurs` prépare la prochaine évolution : fournisseur préféré, référence fournisseur, tarif, délai et minimum de commande par article.
