$ErrorActionPreference = "Stop"

Write-Host "=== Lot AB.1.1 - Fiabilisation des tests backend ===" -ForegroundColor Cyan

Write-Host "`n--- Etat des conteneurs ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Repertoire Python du backend ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'pwd; echo PYTHONPATH=$PYTHONPATH; find /app -maxdepth 3 -type f -name "__init__.py" | head -30'

Write-Host "`n--- Verification import application ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -c "import app; print(\"IMPORT APP : OK ->\", app.__file__)"'

Write-Host "`n--- Verification configuration SQLAlchemy ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -c "from sqlalchemy.orm import configure_mappers; import app.models; configure_mappers(); print(\"MAPPERS : OK\")"'

Write-Host "`n--- Collecte Pytest uniquement ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -m pytest --collect-only -q' 2>&1 |
  Tee-Object -FilePath ".\AB1-PYTEST-COLLECT.txt"

Write-Host "`n--- Suite Pytest ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -m pytest -q' 2>&1 |
  Tee-Object -FilePath ".\AB1-PYTEST-RESULTATS.txt"

Write-Host "`n--- Health final ---" -ForegroundColor Cyan
curl.exe http://127.0.0.1:8000/api/health

Write-Host "`nDeux rapports ont ete crees :" -ForegroundColor Green
Write-Host "  AB1-PYTEST-COLLECT.txt"
Write-Host "  AB1-PYTEST-RESULTATS.txt"
