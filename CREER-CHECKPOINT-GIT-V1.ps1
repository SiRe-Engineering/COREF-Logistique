$ErrorActionPreference = "Stop"

Write-Host "=== AB.3 - Checkpoint Git V1 ===" -ForegroundColor Cyan

# 1. Verify we are inside a Git repository.
git rev-parse --is-inside-work-tree | Out-Null
$branch = git branch --show-current
Write-Host "Branche courante : $branch" -ForegroundColor Cyan

# 2. Safety checks before staging.
Write-Host "`n--- Alembic ---" -ForegroundColor Cyan
docker compose exec backend alembic current

Write-Host "`n--- Suite Pytest ---" -ForegroundColor Cyan
docker compose exec backend sh -lc 'cd /app && python -m pytest -q'

if ($LASTEXITCODE -ne 0) {
    throw "Pytest n'est pas vert. Checkpoint annule."
}

Write-Host "`n--- Health backend ---" -ForegroundColor Cyan
$health = curl.exe -s http://127.0.0.1:8000/api/health
Write-Host $health
if ($LASTEXITCODE -ne 0) {
    throw "Backend non joignable. Checkpoint annule."
}

# 3. Remove only generated diagnostic result files.
$generated = @(
    "AB1-PYTEST-COLLECT.txt",
    "AB1-PYTEST-RESULTATS.txt",
    "AB1-2-PYTEST-RESULTATS.txt",
    "AB1-3-PYTEST-RESULTATS.txt"
)
foreach ($file in $generated) {
    if (Test-Path $file) {
        Remove-Item $file -Force
    }
}

# 4. Show what will be checkpointed.
Write-Host "`n--- Etat Git avant staging ---" -ForegroundColor Cyan
git status --short

# 5. Stage the complete current application state.
git add -A

Write-Host "`n--- Fichiers stages ---" -ForegroundColor Cyan
git status --short

# 6. Refuse an empty checkpoint.
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "Aucun changement a committer. Le depot est deja au checkpoint." -ForegroundColor Yellow
} else {
    git commit -m "release: consolidate COREF Logistique V1"
    if ($LASTEXITCODE -ne 0) {
        throw "Le commit Git a echoue."
    }
}

# 7. Create an annotated local release-candidate tag.
$tag = "v1.0.0-rc1"
$existing = git tag --list $tag
if (-not $existing) {
    git tag -a $tag -m "COREF Logistique V1 consolidated release candidate"
    if ($LASTEXITCODE -ne 0) {
        throw "La creation du tag a echoue."
    }
} else {
    Write-Host "Tag $tag deja present : non recree." -ForegroundColor Yellow
}

# 8. Final verification.
Write-Host "`n--- Checkpoint cree ---" -ForegroundColor Green
git log -1 --oneline
git tag --list "v1.0.0-rc1"

Write-Host "`n--- Etat Git final ---" -ForegroundColor Cyan
git status

Write-Host "`nIMPORTANT : aucun git push n'a ete execute." -ForegroundColor Yellow
Write-Host "Si tout est correct, le push sera fait dans l'etape AB.3.1." -ForegroundColor Yellow
