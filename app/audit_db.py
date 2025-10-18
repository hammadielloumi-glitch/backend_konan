import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import subprocess

print("🔍 Lancement de l'audit Alembic / Base PostgreSQL...\n")

# Charger .env
load_dotenv()

# Récupération URL
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERREUR : aucune variable DATABASE_URL trouvée dans l'environnement.")
    sys.exit(1)

print(f"🔗 DATABASE_URL détectée : {DATABASE_URL}\n")

# Vérification connexion
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connexion PostgreSQL réussie : {version}\n")
except OperationalError as e:
    print(f"❌ ERREUR CONNEXION : {e}")
    sys.exit(1)

# Vérification des tables
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if not tables:
        print("⚠️ Aucune table détectée dans la base.")
        print("➡️ Application automatique des migrations Alembic...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Migrations appliquées avec succès.\n")
    else:
        print(f"✅ Tables existantes : {tables}\n")
except Exception as e:
    print(f"❌ Erreur lors de la vérification des tables : {e}")
    sys.exit(1)

print("🔎 Vérification de la cohérence des révisions Alembic...")
try:
    subprocess.run(["alembic", "current"], check=False)
except Exception as e:
    print(f"⚠️ Impossible d’exécuter alembic current : {e}")

print("\n🎯 Audit terminé avec succès !")
