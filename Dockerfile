# ==========================================
# Dockerfile — Konan Backend (Production)
# ==========================================

FROM python:3.11-slim

WORKDIR /app

# Optimisations d’exécution
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation des dépendances système et client PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev postgresql-client curl \
 && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copie du code source
COPY . /app

# Création du dossier Chroma persisté
RUN mkdir -p /app/chroma_store

# Exposition du port
EXPOSE 8000

# Lancement automatique : attente PostgreSQL → migrations → API
CMD bash -c "\
  echo '🧩 Attente de PostgreSQL...' && \
  until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do \
    echo '⏳ Base non prête, nouvelle tentative...'; \
    sleep 2; \
  done && \
  echo '✅ Base disponible, lancement du backend...' && \
  alembic upgrade head && \
  uvicorn app.main:app --host 0.0.0.0 --port 8000"
