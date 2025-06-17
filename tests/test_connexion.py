from sqlalchemy import text
conn.execute(text("SELECT version();")).fetchone()
DATABASE_URL = "postgresql://log430:laboratoire@localhost:5432/log430" #postgresql://utilisateur:motdepasse@adresse_ip:port/nom_dbcd

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Connexion réussie !")
        print("Version de PostgreSQL :", conn.execute("SELECT version();").fetchone())
except Exception as e:
    print("Erreur de connexion :", e)
