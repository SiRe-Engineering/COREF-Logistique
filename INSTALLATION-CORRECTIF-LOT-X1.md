# Correctif Lot X.1
Corrige la collision PostgreSQL avec la table historique `lignes_inventaire`.

Nouvelles tables :
- `campagnes_inventaire_avance`
- `lignes_inventaire_avance`

La révision reste `0038` car l'échec précédent a laissé Alembic en `0037`.

Après extraction à la racine :
```powershell
powershell -ExecutionPolicy Bypass -File .\APPLIQUER-CORRECTIF-X1.ps1
docker compose down
docker compose up --build -d
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
```
Attendu : `0038 (head)` et health `ok`.

Ne supprimez aucune table existante et n'utilisez pas `docker compose down -v`.
