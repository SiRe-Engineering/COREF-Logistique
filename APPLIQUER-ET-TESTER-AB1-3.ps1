$ErrorActionPreference="Stop"

Write-Host "=== Correctif AB.1.3 - Tests Stock ===" -ForegroundColor Cyan

docker compose up --build -d backend
Start-Sleep -Seconds 2

Write-Host "`n--- Tests Stock uniquement ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -m pytest tests/test_stock_schema.py tests/test_reservation_notification_schema.py -q'

Write-Host "`n--- Suite complete ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -m pytest -q' 2>&1 |
  Tee-Object -FilePath ".\AB1-3-PYTEST-RESULTATS.txt"

Write-Host "`n--- Health ---" -ForegroundColor Cyan
curl.exe http://127.0.0.1:8000/api/health
