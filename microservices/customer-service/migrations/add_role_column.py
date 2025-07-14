#!/usr/bin/env python3
"""
Script de migration pour ajouter le champ role aux utilisateurs existants
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://log430:laboratoire@localhost:5437/customers_db')

def migrate_add_role_column():
    """Ajouter le champ role à la table customers si il n'existe pas"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'role'
            """))
            
            if result.fetchone() is None:
                print("Ajout de la colonne 'role' à la table customers...")
                
                # Ajouter la colonne role
                conn.execute(text("""
                    ALTER TABLE customers 
                    ADD COLUMN role VARCHAR(50) DEFAULT 'client' NOT NULL
                """))
                
                # Mettre à jour les utilisateurs existants avec le rôle par défaut
                conn.execute(text("""
                    UPDATE customers 
                    SET role = 'client' 
                    WHERE role IS NULL OR role = ''
                """))
                
                conn.commit()
                print("Migration terminée avec succès !")
            else:
                print("La colonne 'role' existe déjà dans la table customers.")
                
    except Exception as e:
        print(f"Erreur lors de la migration : {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_add_role_column()
