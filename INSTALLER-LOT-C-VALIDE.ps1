$ErrorActionPreference = "Stop"

$badMigration = "backend\alembic\versions\0022_add_preparation_replacement_history.py"

if (Test-Path $badMigration) {
    Remove-Item $badMigration -Force
    Write-Host "Migration 0022 défectueuse supprimée." -ForegroundColor Green
} else {
    Write-Host "Aucune migration 0022 défectueuse à supprimer." -ForegroundColor Yellow
}

Write-Host "Les fichiers stables du Lot C sont restaurés." -ForegroundColor Green
