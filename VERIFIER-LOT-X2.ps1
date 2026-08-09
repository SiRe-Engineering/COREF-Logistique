$ErrorActionPreference = "Stop"

Write-Host "=== Verification Lot X.2 ===" -ForegroundColor Cyan

docker compose up --build -d backend

Write-Host "`n--- Alembic ---" -ForegroundColor Cyan
docker compose exec backend alembic current

Write-Host "`n--- Import API inventaires avances ---" -ForegroundColor Cyan
docker compose exec backend python -c "from app.api.inventaires_avances import router; print('IMPORT INVENTAIRES AVANCES : OK')"

Write-Host "`n--- Health ---" -ForegroundColor Cyan
curl.exe http://127.0.0.1:8000/api/health

Write-Host "`n--- Derniers logs backend ---" -ForegroundColor Cyan
docker compose logs backend --tail=120
