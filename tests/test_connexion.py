from sqlalchemy import create_engine, text

def test_postgres_connection():
    DATABASE_URL = "postgresql://log430:laboratoire@localhost:5432/log430"
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).fetchone()
            assert version is not None
    except Exception as e:
        assert False, f"Connexion à la BDD impossible: {e}"
