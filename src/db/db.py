
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://log430:laboratoire@localhost:5432/log430" #postgresql://utilisateur:motdepasse@adresse_ip:port/nom_db
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    # Crée les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
