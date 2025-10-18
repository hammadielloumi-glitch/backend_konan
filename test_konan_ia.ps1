# =============================================
# KONAN IA LANGUAGE TEST (ASCII SAFE)
# =============================================

$apiUrl = "http://127.0.0.1:8000/api/chat"
$session_id = "test_auto_lang"
$logFile = "konan_ia_test_log.csv"

"Langue;Message;Duree(s);Reponse" | Out-File -Encoding ASCII $logFile

function TestKonanLang {
    param(
        [string]$lang,
        [string]$message
    )

    Write-Host ""
    Write-Host "==============================="
    Write-Host ("Test langue : " + $lang)
    Write-Host "==============================="

    $body = @{
        session_id = $session_id
        message    = $message
    } | ConvertTo-Json

    $start = Get-Date
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method POST -Body $body -ContentType "application/json"
        $end = Get-Date
        $duration = ($end - $start).TotalSeconds

        $text = $response.response
        Write-Host ""
        Write-Host "Reponse Konan :"
        Write-Host $text
        Write-Host ""
        Write-Host ("Temps de reponse : " + $duration + " s")

        ($lang + ";" + $message + ";" + $duration + ";" + $text) | Out-File -Append -Encoding ASCII $logFile
    }
    catch {
        Write-Host ("Erreur : " + $_.Exception.Message)
        ($lang + ";" + $message + ";ERREUR;") | Out-File -Append -Encoding ASCII $logFile
    }
}

# =========================
# TESTS
# =========================
TestKonanLang -lang "fr" -message "Quelles sont les etapes legales en cas de vol de voiture ?"
TestKonanLang -lang "ar" -message "?? ?? ????????? ????????? ?? ???? ???? ??????"
TestKonanLang -lang "tn" -message "??? ???? ??? ?????? ??????? ??????"

# =========================
# FIN
# =========================
Write-Host ""
Write-Host ("Tests termines. Resultats enregistres dans " + $logFile)
