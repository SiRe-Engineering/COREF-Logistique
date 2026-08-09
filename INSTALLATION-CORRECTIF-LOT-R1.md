# Correctif Lot R.1 — Démarrage backend

## Cause

Le Lot R utilise :

```python
response_model=ReceptionLigneResult
```

dans `backend/app/api/achats.py`, mais `ReceptionLigneResult` n'était pas
importé depuis `app.schemas.achats`.

FastAPI évalue le décorateur au démarrage du backend : le conteneur backend
s'arrête donc avant que `/api/auth/me` puisse répondre.

Le frontend affiche alors :

```text
Error: Failed to fetch
components/auth/AuthProvider.tsx
```

## Correctif

Remplacer uniquement :

```text
backend/app/api/achats.py
```

Aucune migration supplémentaire.

## Relance

```powershell
docker compose up --build -d backend
docker compose ps
docker compose logs backend --tail=150
curl.exe http://127.0.0.1:8000/api/health
```

Le health check doit retourner :

```json
{"status":"ok","database":"connected"}
```

Puis :

```powershell
docker compose up -d frontend
```

et `Ctrl + F5`.

La base doit rester en :

```text
0032 (head)
```
