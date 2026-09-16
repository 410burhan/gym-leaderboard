"""
Run once to create all tables in your Supabase Postgres database.
Usage (from the backend/ folder, with your venv active):
    python create_tables.py
"""
from app.database import Base, engine
from app import models  # noqa: F401 - import registers the models on Base.metadata

Base.metadata.create_all(engine)
print("Tables created (or already existed). Check Supabase's Table Editor to confirm.")