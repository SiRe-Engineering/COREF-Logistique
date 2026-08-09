$ErrorActionPreference = "Stop"

$frontend = Join-Path $PSScriptRoot "frontend"

if (-not (Test-Path $frontend)) {
    Write-Host "Dossier frontend introuvable. Le code principal reste installé." -ForegroundColor Yellow
    exit 0
}

$files = Get-ChildItem $frontend -Recurse -File |
    Where-Object { $_.Extension -in ".tsx", ".ts" }

$modified = 0

foreach ($file in $files) {
$content = [System.IO.File]::ReadAllText($file.FullName)

    if ($content -notmatch "/preparations") {
        continue
    }

    $newContent = $content
    $newContent = $newContent.Replace(
        'label: "Préparations"',
        'label: "Préparations / Retours"'
    )
    $newContent = $newContent.Replace(
        "label: 'Préparations'",
        "label: 'Préparations / Retours'"
    )
    $newContent = $newContent.Replace(
        '>Préparations</',
        '>Préparations / Retours</'
    )

    if ($newContent -ne $content) {
        [System.IO.File]::WriteAllText(
    $file.FullName,
    $newContent,
    [System.Text.UTF8Encoding]::new($false)
)
        Write-Host "Navigation renommée : $($file.FullName)" -ForegroundColor Green
    }
}

if ($modified -eq 0) {
    Write-Host (
        "Aucun libellé global de navigation n’a été trouvé automatiquement. " +
        "La page elle-même est bien renommée."
    ) -ForegroundColor Yellow
}
