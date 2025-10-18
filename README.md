
# Konan Backend (FastAPI)

## Prérequis
- Docker + Docker Compose (recommandé) ou Python 3.11
- OpenAI API key (facultatif pour test hors ligne)

## Démarrage rapide (Docker)
```bash
cp .env.example .env
docker compose up --build
# API: http://127.0.0.1:8000
# Seed: POST http://127.0.0.1:8000/seed
```

## Local sans Docker
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints
- POST /auth/register
- POST /auth/login
- POST /seed
- POST /chat
- POST /pdf
