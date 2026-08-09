$ErrorActionPreference="Stop"

Write-Host "=== Lot AB.2 - Securisation progressive V1 ===" -ForegroundColor Cyan

docker compose up --build -d backend frontend
Start-Sleep -Seconds 3

Write-Host "`n--- Alembic ---" -ForegroundColor Cyan
docker compose exec backend alembic current

Write-Host "`n--- Mappers ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -c "from sqlalchemy.orm import configure_mappers; import app.models; configure_mappers(); print(\"MAPPERS : OK\")"'

Write-Host "`n--- Tests backend ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -m pytest -q'

Write-Host "`n--- Health public ---" -ForegroundColor Cyan
curl.exe http://127.0.0.1:8000/api/health

Write-Host "`n--- API Articles sans jeton : 401 attendu ---" -ForegroundColor Cyan
curl.exe -i http://127.0.0.1:8000/api/articles

Write-Host "`n--- API Stocks sans jeton : 401 attendu ---" -ForegroundColor Cyan
curl.exe -i http://127.0.0.1:8000/api/stocks

Write-Host "`n--- Logs backend ---" -ForegroundColor Cyan
docker compose logs backend --tail=100

Write-Host "`n--- Logs frontend ---" -ForegroundColor Cyan
docker compose logs frontend --tail=100
