$ErrorActionPreference="Stop"

$path="backend/app/models/__init__.py"
$c=Get-Content $path -Raw
$c=$c.Replace(
  "from app.models.inventaire_avance import CampagneInventaire, LigneInventaire",
  "from app.models.inventaire_avance import CampagneInventaireAvance, LigneInventaireAvance"
)
Set-Content $path $c -Encoding UTF8

Write-Host "Imports des modèles Inventaire avancé corrigés." -ForegroundColor Green

docker compose up --build -d backend

Write-Host "`n--- Test configuration SQLAlchemy ---" -ForegroundColor Cyan
docker compose exec backend python -c "from sqlalchemy.orm import configure_mappers; import app.models; configure_mappers(); print('MAPPERS SQLALCHEMY : OK')"

Write-Host "`n--- Test auth ---" -ForegroundColor Cyan
curl.exe -i http://127.0.0.1:8000/api/auth/me

Write-Host "`n--- Health ---" -ForegroundColor Cyan
curl.exe http://127.0.0.1:8000/api/health

Write-Host "`n--- Alembic ---" -ForegroundColor Cyan
docker compose exec backend alembic current
