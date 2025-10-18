# repair_encoding.ps1
$inputFile = "konan_ia_test_log.normalized.csv"
$outputFile = "konan_ia_test_log.repaired.csv"

# Lecture binaire brute (aucune interprétation d'encodage)
[byte[]]$bytes = [System.IO.File]::ReadAllBytes($inputFile)

# 1️⃣ Décodage manuel depuis Windows-1252
$text = [System.Text.Encoding]::GetEncoding(1252).GetString($bytes)

# 2️⃣ Suppression des doubles BOM et séquences parasites
$text = $text -replace "ï»¿", "" -replace "uFEFF", ""

# 3️⃣ Ré-encodage propre en UTF-8 avec BOM
[System.IO.File]::WriteAllText($outputFile, "`uFEFF" + $text, [System.Text.Encoding]::UTF8)

Write-Host ("✅ Fichier réparé : " + $outputFile) -ForegroundColor Green
