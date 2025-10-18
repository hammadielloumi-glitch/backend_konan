# fix_utf8.ps1
$inputFile = "konan_ia_test_log.normalized.csv"
$outputFile = "konan_ia_test_log.fixed.csv"

# Lire brut en bytes
$bytes = [System.IO.File]::ReadAllBytes($inputFile)

# Étape 1 : décodage depuis UTF8 -> texte intermédiaire corrompu
$temp = [System.Text.Encoding]::UTF8.GetString($bytes)

# Étape 2 : redécodage depuis Windows-1252 pour restaurer les accents
$content = [System.Text.Encoding]::GetEncoding(1252).GetString(
    [System.Text.Encoding]::UTF8.GetBytes($temp)
)

# Écriture propre en UTF-8 BOM
[System.IO.File]::WriteAllText($outputFile, "`uFEFF" + $content, [System.Text.Encoding]::UTF8)

Write-Host ("✅ Fichier réparé : " + $outputFile) -ForegroundColor Green
