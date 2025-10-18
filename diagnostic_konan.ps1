# =======================================================
# Diagnostic Complet - Backend Konan (UTF-8 safe)
# =======================================================

Write-Host "`n=== DEMARRAGE DU DIAGNOSTIC KONAN ===`n" -ForegroundColor Cyan

# Étape 1 : Vérifier les conteneurs Docker
Write-Host "Verification des conteneurs actifs..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}"
if ($containers -match "konan_backend" -and $containers -match "konan_db") {
    Write-Host "OK : Containers 'konan_backend' et 'konan_db' actifs." -ForegroundColor Green
} else {
    Write-Host "Containers manquants. Redemarrage..." -ForegroundColor Red
    docker compose down -v
    docker compose up --build -d
    Start-Sleep -Seconds 10
}

# Étape 2 : Vérifier si le backend FastAPI est accessible
Write-Host "`nVerification de l'API FastAPI..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "OK : FastAPI est en ligne (http://localhost:8000/docs)" -ForegroundColor Green
    } else {
        Write-Host "Attention : L'API repond avec le code $($response.StatusCode)" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "Erreur : L'API ne repond pas sur le port 8000." -ForegroundColor Red
}

# Étape 3 : Vérifier la connexion PostgreSQL
Write-Host "`nVerification de la base de donnees PostgreSQL..." -ForegroundColor Yellow
try {
    docker compose exec konan_db psql -U postgres -d konan_db -c "\dt" | Out-Null
    Write-Host "OK : Connexion PostgreSQL reussie." -ForegroundColor Green
} catch {
    Write-Host "Erreur : Connexion a PostgreSQL impossible." -ForegroundColor Red
}

# Étape 4 : Test API Konan (/api/chat)
Write-Host "`nTest de l'endpoint /api/chat..." -ForegroundColor Yellow
$body = @{
    session_id = "test_diagnostic"
    sender     = "user"
    message    = "Quels sont les droits du locataire en Tunisie ?"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
    Write-Host "OK : Reponse de l'API Konan :" -ForegroundColor Green
    $result | ConvertTo-Json | Write-Host
} catch {
    Write-Host "Erreur : Echec du test API /api/chat" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor DarkGray
}

# Étape 5 : Résumé final
Write-Host "`n=== DIAGNOSTIC TERMINE ===" -ForegroundColor Cyan
