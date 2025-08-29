
#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER","autotestai")
    password = os.getenv("POSTGRES_PASSWORD","autotestai_pass")
    host = os.getenv("DB_HOST","db")
    port = os.getenv("POSTGRES_PORT","5432")
    db = os.getenv("POSTGRES_DB","autotestai_db")
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
print("Using DB URL:", DATABASE_URL)
engine = create_engine(DATABASE_URL)
sql = open("database/seed_supabase.sql").read()
with engine.begin() as conn:
    conn.execute(text(sql))
print("Seed complete.")
