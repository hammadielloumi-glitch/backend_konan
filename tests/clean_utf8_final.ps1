# clean_utf8_final.ps1
param(
    [string]$InputFile = ".\konan_ia_test_log.repaired.csv",
    [string]$OutputFile = ".\konan_ia_test_log.clean.csv"
)

if (-not (Test-Path $InputFile)) {
    Write-Host "❌ Fichier introuvable : $InputFile" -ForegroundColor Red
    exit 1
}

# Lecture binaire et suppression du BOM
$bytes = Get-Content -Path $InputFile -Encoding Byte
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    $bytes = $bytes[3..($bytes.Length - 1)]
}

# Reconvertir proprement (Windows-1252 → UTF-8)
$text = [System.Text.Encoding]::UTF8.GetString(
    [System.Text.Encoding]::Convert([System.Text.Encoding]::GetEncoding(1252), [System.Text.Encoding]::UTF8, $bytes)
)

# Écriture finale en UTF-8 sans double BOM
[System.IO.File]::WriteAllText($OutputFile, $text, [System.Text.Encoding]::UTF8)
Write-Host "✅ Fichier propre enregistré : $OutputFile" -ForegroundColor Green
