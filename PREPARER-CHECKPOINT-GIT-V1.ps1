$ErrorActionPreference="Stop"
Write-Host "=== Preparation checkpoint V1 ===" -ForegroundColor Cyan
git status
Write-Host "`nSi la recette AB est valide, les commandes recommandees seront :" -ForegroundColor Yellow
Write-Host "git add ."
Write-Host 'git commit -m "release: consolidate COREF Logistique V1"'
Write-Host "git status"
Write-Host "`nAucune commande Git n'a ete executee automatiquement." -ForegroundColor Green
