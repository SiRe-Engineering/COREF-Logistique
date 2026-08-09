$ErrorActionPreference="Stop"

# API
$path="backend/app/api/__init__.py"; $c=Get-Content $path -Raw
if($c -notmatch "alertes_logistiques import"){
  $c="from app.api.alertes_logistiques import router as alertes_logistiques_router`r`n"+$c
  Set-Content $path $c -Encoding UTF8
}

$path="backend/app/main.py"; $c=Get-Content $path -Raw
if($c -notmatch "app.include_router\(alertes_logistiques_router\)"){
  $c="from app.api.alertes_logistiques import router as alertes_logistiques_router`r`n"+$c+"`r`napp.include_router(alertes_logistiques_router)`r`n"
  Set-Content $path $c -Encoding UTF8
}

Write-Host "Lot Y raccorde." -ForegroundColor Green
docker compose up --build -d backend frontend
Start-Sleep -Seconds 3
docker compose exec backend python -c "from app.api.alertes_logistiques import router; print('API ALERTES : OK')"
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=80
