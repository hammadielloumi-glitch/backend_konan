# ===========================================
# 🚀 KONAN BACKEND TEST & DEPLOY SCRIPT
# Auteur : Boss (Mhamed Elloumi)
# Version : 1.0
# Description : Rebuild complet du backend Konan + Test API automatique
# ===========================================

Write-Host "`n============================" -ForegroundColor Cyan
Write-Host "   Lancement du backend KONAN" -ForegroundColor Green
Write-Host "============================`n" -ForegroundColor Cyan

# Étape 1. Nettoyage complet des conteneurs et volumes
Write-Host "🧹 Suppression des anciens conteneurs et volumes..." -ForegroundColor Yellow
docker compose down -v
docker system prune -a --volumes -f
Write-Host "✅ Nettoyage terminé.`n" -ForegroundColor Green

# Étape 2. Reconstruction complète
Write-Host "🛠️ Reconstruction des conteneurs Docker..." -ForegroundColor Yellow
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur de build !" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build terminé.`n" -ForegroundColor Green

# Pause pour laisser PostgreSQL démarrer
Write-Host "⏳ Attente du démarrage des services (15 secondes)..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Étape 3. Vérification de l’état des conteneurs
Write-Host "🔍 Vérification du statut des conteneurs..." -ForegroundColor Yellow
docker ps
Write-Host "`n✅ Conteneurs en ligne.`n" -ForegroundColor Green

# Étape 4. Test automatique de l’API /api/chat
Write-Host "✅ Test de l’API Konan (POST /api/chat)..." -ForegroundColor Cyan

$Body = @{
    session_id = "test-001"
    sender     = "user"
    message    = "Quels sont les droits du locataire en Tunisie ?"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -ContentType "application/json" -Body $Body
    Write-Host "`n✅ Réponse API reçue :" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
}
catch {
    Write-Host "`n⚠️ Erreur de connexion à l’API Konan !" -ForegroundColor Red
    Write-Host "Vérifie que le backend est bien en cours d’exécution sur le port 8000." -ForegroundColor DarkYellow
}

