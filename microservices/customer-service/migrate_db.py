"""
Script pour migrer la base de données et ajouter les colonnes manquantes
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@localhost:5437/customers_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_database():
    """Migrer la base de données avec les nouvelles colonnes"""
    session = SessionLocal()
    
    try:
        # Vérifier si la table existe
        result = session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'customers')"))
        table_exists = result.scalar()
        
        if not table_exists:
            logger.info("La table customers n'existe pas. Création via SQLAlchemy...")
            from src.infrastructure.database.models import Base
            Base.metadata.create_all(bind=engine)
            logger.info("Tables créées avec succès")
        else:
            logger.info("La table customers existe déjà")
            
            # Vérifier et ajouter la colonne role si elle n'existe pas
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'role'
            """))
            
            if not result.fetchone():
                logger.info("Ajout de la colonne 'role'...")
                session.execute(text("ALTER TABLE customers ADD COLUMN role VARCHAR(50) DEFAULT 'client'"))
                session.commit()
                logger.info("Colonne 'role' ajoutée avec succès")
            
            # Vérifier et ajouter la colonne store_id si elle n'existe pas
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'store_id'
            """))
            
            if not result.fetchone():
                logger.info("Ajout de la colonne 'store_id'...")
                session.execute(text("ALTER TABLE customers ADD COLUMN store_id INTEGER"))
                session.commit()
                logger.info("Colonne 'store_id' ajoutée avec succès")
        
        logger.info("Migration terminée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_database()
