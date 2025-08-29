
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text, create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER", "autotestai")
    password = os.getenv("POSTGRES_PASSWORD", "autotestai_pass")
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "autotestai_db")
    DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def init_db():
    # Create tables using sync engine to run schema.sql
    sync_db_url = DATABASE_URL.replace("asyncpg", "psycopg2")
    sync_engine = create_engine(sync_db_url)
    with sync_engine.connect() as conn:
        schema = open("database/schema.sql").read()
        conn.execute(text(schema))
        conn.commit()
