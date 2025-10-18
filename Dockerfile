# ==========================================
# Dockerfile — Konan Backend (Render Ready)
# ==========================================

FROM python:3.11-slim

WORKDIR /app

# Configuration environnementale
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev postgresql-client curl \
 && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copie du code source
COPY . .

# Création du répertoire Chroma persisté
RUN mkdir -p /app/chroma_store

# Commande Render-ready (port dynamique)
CMD bash -lc "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
