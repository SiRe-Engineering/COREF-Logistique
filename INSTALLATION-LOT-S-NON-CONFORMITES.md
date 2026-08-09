# Lot S — Non-conformités fournisseurs

Migration : `0033` après `0032`.

## Fonctions
- NCF automatique `NCF-000001`.
- Création uniquement à partir d'une réception fournisseur sous réserve ou non conforme.
- Commande, fournisseur, article et lot repris automatiquement.
- Quantité concernée, description et responsable.
- Décisions : accepté en l'état, tri, retour fournisseur, remplacement, avoir.
- Statuts : ouverte, en traitement, clôturée.
- Une décision est obligatoire pour clôturer.
- L'écran Contrôles réception indique si une NCF existe.
- Nouveau module `/achats/non-conformites`.
- Nouveau tableau Qualité fournisseurs dans Pilotage achats : réceptions, NCF, NCF ouvertes et taux NCF.

## Installation
```powershell
docker compose down
docker compose up --build -d
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```
Ne pas utiliser `-v`.

Attendu : `0033 (head)`.

Puis `Ctrl + F5`.

## Recette
1. Créer une réception `SOUS RÉSERVE` ou `NON CONFORME`.
2. Ouvrir Non-conformités et créer la NCF depuis cette réception.
3. Vérifier `NCF-000001` et les données reprises automatiquement.
4. Passer la NCF en traitement.
5. Choisir une décision puis clôturer.
6. Vérifier Pilotage achats > Qualité fournisseurs.
