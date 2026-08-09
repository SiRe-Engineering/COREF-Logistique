# Lot O — Pilotage Achats & Performance Fournisseurs
Base contrôlée : migration `0029`.

Aucune nouvelle migration.

```powershell
docker compose down
docker compose up --build -d
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```
Ne pas utiliser `-v`. Attendu : `0029 (head)`. Puis `Ctrl + F5`.

Recette : ouvrir `Fournisseurs / Achats` puis `Pilotage achats`, vérifier KPI,
livraisons, retards, performance fournisseurs, évolution des prix et
référentiel à compléter.

Le taux de service est volontairement indiqué comme provisoire tant que la date
réelle de réception finale n'est pas persistée.

Après validation :
```powershell
git status
git add .
git commit -m "feat: add purchasing performance dashboard"
git push
```
