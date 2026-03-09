# python
# s-p500-analysis/sp500_back/database_connect.py
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DB_USER = os.getenv("DB_USER", "sp500_main")
DB_PASSWORD = os.getenv("DB_PASSWORD", "sp500_main")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "sp500")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# Engine SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance FastAPI / utilitaire pour obtenir une session
def get_db() -> Generator:
    with Session(engine) as db:
        yield db