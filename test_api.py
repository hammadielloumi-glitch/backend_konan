import requests

BASE_URL = "http://127.0.0.1:8000/api"  # adapte si nécessaire

# === 1. Seed de la base ===
print("▶️ Test /seed ...")
resp = requests.post(f"{BASE_URL}/seed")
print("Status:", resp.status_code)
print("Response:", resp.json(), "\n")

# === 2. Chat ===
print("▶️ Test /chat ...")
payload = {
    "message": "Quels sont les droits du travailleur ?",
    "domain": "travail",
    "history": []
}
resp = requests.post(f"{BASE_URL}/chat", json=payload)
print("Status:", resp.status_code)
print("Response:", resp.json(), "\n")

# === 3. PDF ===
print("▶️ Test /pdf ...")
payload = {
    "filename": "test_doc",
    "content": "Ceci est un test PDF généré par Konan."
}
resp = requests.post(f"{BASE_URL}/pdf", json=payload)

if resp.status_code == 200:
    with open("test_doc.pdf", "wb") as f:
        f.write(resp.content)
    print("✅ PDF téléchargé : test_doc.pdf\n")
else:
    print("❌ Erreur PDF:", resp.status_code, resp.text)
