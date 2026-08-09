$ErrorActionPreference="Stop"
$path="backend/app/models/__init__.py"; $c=Get-Content $path -Raw
if($c -notmatch "inventaire_avance import"){Set-Content $path ("from app.models.inventaire_avance import CampagneInventaire, LigneInventaire`r`n"+$c) -Encoding UTF8}
$path="backend/app/api/__init__.py"; $c=Get-Content $path -Raw
if($c -notmatch "inventaires_avances import"){Set-Content $path ("from app.api.inventaires_avances import router as inventaires_avances_router`r`n"+$c) -Encoding UTF8}
$path="backend/app/main.py"; $c=Get-Content $path -Raw
if($c -notmatch "app.include_router\(inventaires_avances_router\)"){
  $c="from app.api.inventaires_avances import router as inventaires_avances_router`r`n"+$c+"`r`napp.include_router(inventaires_avances_router)`r`n"
  Set-Content $path $c -Encoding UTF8
}
Write-Host "Correctif X.1 raccorde." -ForegroundColor Green
