# Script pour démarrer le backend Konan
Write-Host "=== Lancement du backend Konan ==="

# Aller à la racine du projet (là où se trouve .env et requirements.txt)
cd "$PSScriptRoot\\.."

# Lancer Uvicorn avec le chemin vers app/main.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload