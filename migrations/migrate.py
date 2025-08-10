from sqlalchemy import create_engine, text

import app.models
from app.config.database import Base
from app.config.settings import settings

def create_database_if_not_exists():
    default_url = str(settings.DATABASE_URL).replace("+asyncpg", "").replace(settings.POSTGRES_DB, "postgres")
    db_name = settings.POSTGRES_DB

    default_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
    with default_engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname=:name"), {"name": db_name}
        )
        exists = result.scalar() is not None

        if not exists:
            print(f"Database '{db_name}' does not exist. Creating...")
            connection.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")

def create_tables():
    create_database_if_not_exists()

    ds = str(settings.DATABASE_URL).replace("+asyncpg", "")
    engine = create_engine(ds, echo=True)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
