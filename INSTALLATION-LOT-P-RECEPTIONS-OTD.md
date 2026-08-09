# Lot P — Réception fournisseur & OTD réel

Migration `0030` après `0029`.

Nouvelles dates persistées :
- première réception de commande ;
- réception finale de commande ;
- première/dernière réception de chaque ligne.

Le Lot O calcule désormais un OTD réel :
`date_reception_finale <= date_livraison_prevue`.

Les commandes historiques clôturées avant le Lot P ne sont pas rétroactivement
incluses dans l'OTD, car leur date réelle de réception n'existe pas.

Installation :
```powershell
docker compose down
docker compose up --build -d
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```
Ne pas utiliser `-v`. Attendu : `0030 (head)`. Puis `Ctrl + F5`.

Recette : créer une commande avec date prévue, faire une réception partielle,
puis finale, vérifier le statut RECUE et ensuite Pilotage achats → OTD /
Performance fournisseurs / Écarts réception.

Après validation :
```powershell
git status
git add .
git commit -m "feat: add real supplier receipt dates and OTD"
git push
```
