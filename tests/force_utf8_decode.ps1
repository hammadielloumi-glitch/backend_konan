# force_utf8_decode.ps1
$inputFile = "konan_ia_test_log.normalized.csv"
$outputFile = "konan_ia_test_log.fixed.csv"

# Lecture brute (bytes)
$bytes = [System.IO.File]::ReadAllBytes($inputFile)

# Décodage manuel depuis Windows-1252
$content = [System.Text.Encoding]::GetEncoding(1252).GetString($bytes)

# Réencodage propre en UTF-8 BOM
[System.IO.File]::WriteAllText($outputFile, "`uFEFF" + $content, [System.Text.Encoding]::UTF8)

Write-Host ("Fichier corrigé enregistré sous : " + $outputFile) -ForegroundColor Green
