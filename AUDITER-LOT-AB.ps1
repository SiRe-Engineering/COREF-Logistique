$ErrorActionPreference="Stop"
Write-Host "=== Lot AB - Audit securite V1 ===" -ForegroundColor Cyan

Write-Host "`n--- Etat Git ---" -ForegroundColor Cyan
git status --short

Write-Host "`n--- Fetch frontend sans entetesAuthentifiees sur la meme ligne ---" -ForegroundColor Cyan
Get-ChildItem frontend -Recurse -Include *.ts,*.tsx |
  Select-String -Pattern "fetch\(" |
  Where-Object { $_.Line -notmatch "entetesAuthentifiees|Authorization" } |
  ForEach-Object { "$($_.Path.Replace((Get-Location).Path + '\','')):$($_.LineNumber): $($_.Line.Trim())" }

Write-Host "`n--- Routes backend utilisant utilisateur_courant ---" -ForegroundColor Cyan
Get-ChildItem backend/app/api -Filter *.py |
  Select-String -Pattern "utilisateur_courant" |
  ForEach-Object { "$($_.Path.Replace((Get-Location).Path + '\','')):$($_.LineNumber)" }

Write-Host "`n--- Tests backend ---" -ForegroundColor Cyan
docker compose exec backend pytest -q
