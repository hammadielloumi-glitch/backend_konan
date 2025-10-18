param(
  [string]$ProjectPath = "$PSScriptRoot"
)

Write-Host "== Konan backend refresh ==" -ForegroundColor Cyan
Set-Location $ProjectPath

# 1) Sanity checks
if (-not (Test-Path "$ProjectPath\docker-compose.yml")) {
  Write-Error "docker-compose.yml introuvable dans $ProjectPath"
  exit 1
}
if (-not (Test-Path "$ProjectPath\Dockerfile")) {
  Write-Error "Dockerfile introuvable dans $ProjectPath. Vérifie le nom exact (sans .txt)."
  exit 1
}
if (-not (Test-Path "$ProjectPath\requirements.txt")) {
  Write-Error "requirements.txt introuvable dans $ProjectPath"
  exit 1
}

Write-Host "`n[1/6] docker compose config (validation)" -ForegroundColor Yellow
docker compose -f "$ProjectPath\docker-compose.yml" config || exit 1

Write-Host "`n[2/6] Stop + purge volumes & orphelins" -ForegroundColor Yellow
docker compose -f "$ProjectPath\docker-compose.yml" down -v --remove-orphans

Write-Host "`n[3/6] Nettoyage builder cache (optionnel)" -ForegroundColor Yellow
docker builder prune -f | Out-Null

Write-Host "`n[4/6] Build sans cache (journal détaillé)" -ForegroundColor Yellow
docker compose -f "$ProjectPath\docker-compose.yml" build --no-cache --progress=plain || exit 1

Write-Host "`n[5/6] Démarrage en détaché" -ForegroundColor Yellow
docker compose -f "$ProjectPath\docker-compose.yml" up -d || exit 1

Start-Sleep -Seconds 5

Write-Host "`n[6/6] Derniers logs backend" -ForegroundColor Yellow
docker compose -f "$ProjectPath\docker-compose.yml" logs backend --tail=80

Write-Host "`n== Tests HTTP ==" -ForegroundColor Cyan
$local = "http://localhost:8000/health"
try {
  $r1 = Invoke-WebRequest -Uri $local -UseBasicParsing -TimeoutSec 5
  Write-Host "GET $local -> $($r1.StatusCode)" -ForegroundColor Green
  Write-Host $r1.Content
} catch {
  Write-Warning "Echec GET $local : $($_.Exception.Message)"
}

# Détecter IP Wi-Fi Windows
$wifi = (Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null -and $_.NetAdapter.Status -eq "Up" } | Select-Object -First 1)
if ($wifi -and $wifi.IPv4Address.IPAddress) {
  $ip = $wifi.IPv4Address.IPAddress
  $lan = "http://$ip:8000/health"
  try {
    $r2 = Invoke-WebRequest -Uri $lan -UseBasicParsing -TimeoutSec 5
    Write-Host "GET $lan -> $($r2.StatusCode)" -ForegroundColor Green
    Write-Host $r2.Content
  } catch {
    Write-Warning "Echec GET $lan : $($_.Exception.Message)"
  }
} else {
  Write-Warning "IP Wi-Fi non détectée automatiquement."
}

Write-Host "`nTerminé. Si 'Could not import module' apparaît, vérifie que la commande uvicorn est 'app.main:app'." -ForegroundColor Cyan
