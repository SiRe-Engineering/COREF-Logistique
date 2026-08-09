# Lot T — Retours fournisseurs, avoirs & remplacements
Migration `0034` après `0033`.

## Principes
Une décision NCF n'effectue jamais seule un mouvement de stock.
Le mouvement est déclenché uniquement lorsque l'opérateur valide le retour physique ou le rebut après tri.

## Fonctions
- dossier automatique `RET-000001` depuis une NCF ayant une décision ;
- retour fournisseur avec choix de l'emplacement et sortie de stock tracée ;
- remplacement : retour physique puis rapprochement avec une nouvelle réception du même article/fournisseur ;
- avoir : référence, montant HT, date, suivi attendu/reçu ;
- tri : quantité conforme + quantité rebutée = quantité NCF, sortie de stock du rebut ;
- accepté en l'état : clôture sans mouvement ;
- vue `Fournisseurs / Achats / Retours & litiges`.

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
Attendu : `0034 (head)`.
Puis `Ctrl + F5`.

## Recette recommandée
1. NCF > décision RETOUR FOURNISSEUR.
2. Ouvrir Retours & litiges et créer le dossier.
3. Vérifier qu'aucun stock n'a encore bougé.
4. Valider le retour physique depuis un emplacement ayant du stock.
5. Vérifier la sortie dans les mouvements et la baisse du stock.
6. Tester AVOIR.
7. Tester TRI avec une quantité rebutée.
8. Tester REMPLACEMENT : retour, nouvelle réception, rapprochement, clôture.
