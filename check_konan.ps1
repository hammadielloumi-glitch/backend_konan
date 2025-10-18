# ============================================
# check_konan.ps1 — Diagnostic complet Konan
# Compatible Windows / Linux / macOS (UTF-8)
# ============================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = New-Object -TypeName System.Text.UTF8Encoding

Write-Host "`n=== DEMARRAGE DU DIAGNOSTIC API KONAN ===`n"

# ---------- CONFIG ----------
$baseUrl = "http://localhost:8000"
$report = @{
    FastAPI = "❌"
    PostgreSQL = "❌"
    ChromaDB = "❌"
    MemoryVector = "❌"
}

# ---------- 1) DOCKER ----------
try {
    $backend = docker ps --filter "name=konan_backend" --format "{{.Names}}"
    $db = docker ps --filter "name=konan_db" --format "{{.Names}}"
    if ($backend -and $db) {
        Write-Host "[OK] Conteneurs Docker -> Backend et base de données actifs"
    } else {
        Write-Host "[ERREUR] Docker -> Un conteneur requis est inactif"
    }
}
catch { Write-Host "[ERREUR] Docker non disponible" }

# ---------- 2) FASTAPI ----------
try {
    $res = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing
    if ($res.StatusCode -eq 200) {
        Write-Host "[OK] FastAPI -> API en ligne et fonctionnelle"
        $report.FastAPI = "✅ OK"
    } else { Write-Host "[ERREUR] FastAPI -> Échec" }
}
catch { Write-Host "[ERREUR] FastAPI non accessible" }

# ---------- 3) POSTGRESQL ----------
try {
    $dbres = Invoke-WebRequest -Uri "$baseUrl/test_db" -UseBasicParsing
    if ($dbres.StatusCode -eq 200) {
        Write-Host "[OK] PostgreSQL -> Connexion réussie à la base"
        $report.PostgreSQL = "✅ OK"
    } else { Write-Host "[ERREUR] PostgreSQL -> Connexion échouée" }
}
catch { Write-Host "[ERREUR] PostgreSQL -> Impossible de se connecter" }

# ---------- 4) CHROMADB ----------
try {
    $ping = Invoke-WebRequest -Uri "$baseUrl/api/memory/ping" -UseBasicParsing
    if ($ping.StatusCode -eq 200) {
        Write-Host "[OK] ChromaDB -> ChromaDB répond - en ligne"
        $report.ChromaDB = "✅ OK"
    } else { Write-Host "[ERREUR] ChromaDB non joignable" }
}
catch { Write-Host "[ERREUR] ChromaDB -> Erreur d'accès" }

# ---------- 5) MÉMOIRE VECTORIELLE ----------
try {
    $test = Invoke-WebRequest -Uri "$baseUrl/api/memory/test" -UseBasicParsing
    if ($test.StatusCode -eq 200) {
        $json = $test.Content | ConvertFrom-Json
        Write-Host "[OK] Mémoire vectorielle -> Test Chroma réussi : $($json.inserted_id)"
        $report.MemoryVector = "✅ OK"
    } else {
        Write-Host "[ERREUR] Mémoire vectorielle -> Test échoué"
    }
}
catch { Write-Host "[ERREUR] Mémoire vectorielle -> Erreur pendant le test" }

# ---------- RAPPORT FINAL ----------
Write-Host "`n=== RAPPORT GLOBAL ==="
$report.GetEnumerator() | ForEach-Object { Write-Host "$($_.Key) : $($_.Value)" }

# ---------- EXPORT JSON ----------
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$filename = "konan_diagnostic_$timestamp.json"
$report | ConvertTo-Json | Out-File -Encoding utf8 $filename

Write-Host "`nRapport exporté vers : .\$filename"
Write-Host "`n=== DIAGNOSTIC TERMINE AVEC SUCCES ==="
