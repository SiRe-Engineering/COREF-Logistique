# Lot W — Documents & conformité matériel
Migration `0037` après `0036`.

Le stockage reprend le mécanisme déjà utilisé par les documents fournisseurs :
contenu binaire en base PostgreSQL. Aucun volume Docker supplémentaire n'est nécessaire.

Fonctions : PDF/images, 15 Mo max, contrôle/certificat/notice/rapport/étalonnage/
assurance/autre, référence, organisme, dates, expiration, téléchargement, suppression,
KPI expirés et échéances à 30 jours.

Installation :
```powershell
docker compose down
docker compose up --build -d
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```
Ne pas utiliser `-v`. Attendu : `0037 (head)`. Puis `Ctrl + F5`.
