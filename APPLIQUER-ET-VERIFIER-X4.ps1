$ErrorActionPreference="Stop"

# Corrige l'import des modèles dans __init__.py.
$path="backend/app/models/__init__.py"
$c=Get-Content $path -Raw

$c=$c.Replace(
  "from app.models.inventaire_avance import CampagneInventaire, LigneInventaire",
  "from app.models.inventaire_avance import CampagneInventaireAvance, LigneInventaireAvance"
)

if($c -notmatch "CampagneInventaireAvance"){
  $c="from app.models.inventaire_avance import CampagneInventaireAvance, LigneInventaireAvance`r`n"+$c
}

Set-Content $path $c -Encoding UTF8

Write-Host "Modele ORM Inventaire avance corrige." -ForegroundColor Green

docker compose up --build -d backend

Start-Sleep -Seconds 3

Write-Host "`n--- Etat conteneurs ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Test import modele ---" -ForegroundColor Cyan
docker compose exec backend python -c "from app.models.inventaire_avance import CampagneInventaireAvance, LigneInventaireAvance; print(CampagneInventaireAvance.__tablename__, LigneInventaireAvance.__tablename__)"

Write-Host "`n--- Test configuration SQLAlchemy ---" -ForegroundColor Cyan
docker compose exec backend python -c "from sqlalchemy.orm import configure_mappers; import app.models; configure_mappers(); print('MAPPERS SQLALCHEMY : OK')"

Write-Host "`n--- Health ---" -ForegroundColor Cyan
curl.exe http://127.0.0.1:8000/api/health

Write-Host "`n--- Alembic ---" -ForegroundColor Cyan
docker compose exec backend alembic current

Write-Host "`n--- Logs backend ---" -ForegroundColor Cyan
docker compose logs backend --tail=120
