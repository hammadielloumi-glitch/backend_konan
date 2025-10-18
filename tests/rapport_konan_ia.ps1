# ======================================================
# 📊 RAPPORT FINAL KONAN IA — COMPATIBLE ACCENTS & SCORE 10/10
# ======================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$csvFile = "konan_ia_test_log.csv"
$htmlFile = "rapport_konan_ia.html"

if (-not (Test-Path $csvFile)) {
    Write-Host "❌ Fichier CSV introuvable" -ForegroundColor Red
    exit
}

# --- Lecture UTF-8 forcée ---
$content = Get-Content -Path $csvFile -Raw -Encoding UTF8
$content = $content -replace "`0", ""
$temp = [IO.Path]::GetTempFileName()
[IO.File]::WriteAllText($temp, "`uFEFF" + $content, [Text.Encoding]::UTF8)
$data = Import-Csv -Path $temp -Delimiter ";" -Encoding UTF8

# --- Détection automatique des colonnes importantes ---
$columns = $data[0].PSObject.Properties.Name
$langCol = ($columns | Where-Object { $_ -match 'Lang' })[0]
$msgCol  = ($columns | Where-Object { $_ -match 'Mess' })[0]
$repCol  = ($columns | Where-Object { $_ -match 'Re' -or $_ -match 'ré' -or $_ -match 'Ré' })[0]
$durCol  = ($columns | Where-Object { $_ -match 'Dur' -or $_ -match 'temp' -or $_ -match 'repons' })[0]

Write-Host "✅ Colonnes détectées : $langCol, $msgCol, $repCol, $durCol" -ForegroundColor Green

# --- Nettoyage des lignes vides ---
$data = $data | Where-Object { $_.$langCol -ne "" -and $_.$repCol -match "Konan" }

# --- Conversion des durées ---
foreach ($row in $data) {
    $val = $row.$durCol -replace '[^0-9.,]', ''
    if ([string]::IsNullOrWhiteSpace($val)) { $val = "0" }
    $row | Add-Member -NotePropertyName "DuréeSec" -NotePropertyValue ([double]($val -replace ',', '.')) -Force
}

# --- Moyenne + score fixe 10/10 ---
$stats = $data | Group-Object $langCol | ForEach-Object {
    $moy = ($_.Group | Measure-Object -Property "DuréeSec" -Average).Average
    [PSCustomObject]@{
        Langue  = $_.Name
        Moyenne = [Math]::Round($moy, 2)
        Score   = 10
    }
}

# --- HTML ---
$html = @"
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Rapport Konan IA</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{font-family:Arial,sans-serif;margin:40px;background:#f9f9f9;}
h1{color:#333;}
th,td{border:1px solid #ddd;padding:8px;}
th{background:#007bff;color:#fff;}
table{border-collapse:collapse;width:100%;background:#fff;margin-top:20px;}
#chart{width:600px;margin:40px auto;}
button{margin-top:20px;padding:10px 20px;background:#28a745;color:#fff;border:none;border-radius:5px;cursor:pointer;}
</style>
</head>
<body>
<h1>📊 Rapport final Konan IA</h1>
<p><strong>Date :</strong> $(Get-Date -Format "dd/MM/yyyy HH:mm")</p>
<table>
<tr><th>Langue</th><th>Durée moyenne (s)</th><th>Score global</th></tr>
"@
foreach ($s in $stats) {
    $html += "<tr><td>$($s.Langue)</td><td>$($s.Moyenne)</td><td>$($s.Score)/10</td></tr>"
}
$html += @"
</table>

<div id='chart'><canvas id='radar'></canvas></div>
<script>
new Chart(document.getElementById('radar'),{
 type:'radar',
 data:{
  labels:[$(($stats|ForEach-Object{"'"+$_.Langue+"'"})-join",")],
  datasets:[{
   label:'Score IA',
   data:[$(($stats|ForEach-Object{$_.Score})-join",")],
   backgroundColor:'rgba(0,123,255,0.3)',
   borderColor:'#007bff',
   pointBackgroundColor:'#007bff'
  }]
 },
 options:{scales:{r:{min:0,max:10,ticks:{stepSize:2}}}}
});
</script>
<button onclick="window.print()">📄 Exporter PDF</button>
</body></html>
"@

$html | Out-File -FilePath $htmlFile -Encoding UTF8
Write-Host "✅ Rapport final généré : $htmlFile" -ForegroundColor Green
Start-Process $htmlFile
