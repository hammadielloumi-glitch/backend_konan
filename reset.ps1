# Stoppe tous les processus uvicorn en cours
Get-Process uvicorn -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.Id -Force }

# Supprime le dossier ChromaDB (s’il existe)
if (Test-Path ".\chroma_store") {
    Remove-Item -Recurse -Force ".\chroma_store"
    Write-Host "✅ Dossier chroma_store supprimé."
} else {
    Write-Host "ℹ️ Aucun dossier chroma_store trouvé, rien à supprimer."
}

# Relance le serveur Uvicorn
Write-Host "🚀 Lancement de l'API Konan..."
uvicorn app.main:app --reload
