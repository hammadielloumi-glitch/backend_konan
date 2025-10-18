# normalize_csv.ps1
param (
    [string]$InputFile,
    [string]$OutputFile
)

# Recherche automatique du fichier CSV si non spécifié
if (-not $InputFile) {
    $csvFiles = Get-ChildItem -Path . -Filter *.csv
    if ($csvFiles.Count -eq 0) {
        Write-Host "Aucun fichier .csv trouvé dans le dossier courant." -ForegroundColor Red
        exit 1
    }
    $InputFile = $csvFiles[0].FullName
    Write-Host ("Fichier détecté : " + $InputFile) -ForegroundColor Yellow
}

# Création du nom de sortie si non spécifié
if (-not $OutputFile) {
    $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, ".csv")
}

# Lecture du contenu
$content = Get-Content -Raw -Path $InputFile -Encoding UTF8

# Table de remplacement des caractères problématiques
$replacements = @{
    ([char]0x2019) = "'"    # Apostrophe typographique
    ([char]0x2018) = "'"    # Apostrophe ouvrante
    ([char]0x2013) = "-"    # Tiret moyen
    ([char]0x2014) = "-"    # Tiret long
    ([char]0x0153) = "oe"   # Ligature œ
    ([char]0x00E9) = "e"    # é
    ([char]0x00E8) = "e"    # è
    ([char]0x00EA) = "e"    # ê
    ([char]0x00C9) = "E"    # É
    ([char]0x00A0) = " "    # Espace insécable
}

# Application des remplacements
foreach ($pair in $replacements.GetEnumerator()) {
    $content = $content -replace [regex]::Escape($pair.Key), $pair.Value
}

# Écriture du fichier normalisé (UTF8 BOM)
[System.IO.File]::WriteAllText($OutputFile, "`uFEFF" + $content, [System.Text.Encoding]::UTF8)

Write-Host ("Normalisation terminée : " + $OutputFile) -ForegroundColor Green
