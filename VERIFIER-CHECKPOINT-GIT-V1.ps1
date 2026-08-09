$ErrorActionPreference = "Stop"

Write-Host "=== Verification checkpoint V1 ===" -ForegroundColor Cyan
Write-Host "`nDernier commit :" -ForegroundColor Cyan
git log -1 --oneline

Write-Host "`nTag V1 RC :" -ForegroundColor Cyan
git tag --list "v1.0.0-rc1"

Write-Host "`nEtat Git :" -ForegroundColor Cyan
git status --short

Write-Host "`nMigrations :" -ForegroundColor Cyan
docker compose exec backend alembic current

Write-Host "`nTests :" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -m pytest -q'
