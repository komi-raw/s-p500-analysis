#!/usr/bin/env python3
"""Script de test pour vérifier la connexion à la base de données MySQL."""

from sqlalchemy import text
from database_connect import engine, SessionLocal

def test_engine_connect():
    """Test de connexion avec l'engine SQLAlchemy."""
    try:
        with engine.connect() as conn:
            val = conn.execute(text("SELECT 1")).scalar()
            print("✓ Engine: connexion OK, SELECT 1 ->", val)
            return True
    except Exception as e:
        print("✗ Engine: connexion ÉCHOUÉE:")
        print(f"  Erreur: {type(e).__name__}: {e}")
        return False

def test_session_connect():
    """Test de connexion avec une session SQLAlchemy."""
    try:
        db = SessionLocal()
        val = db.execute(text("SELECT 1")).scalar()
        print("✓ Session: connexion OK, SELECT 1 ->", val)
        db.close()
        return True
    except Exception as e:
        print("✗ Session: connexion ÉCHOUÉE:")
        print(f"  Erreur: {type(e).__name__}: {e}")
        return False

def test_database_tables():
    """Test pour lister les tables de la base de données."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"✓ Tables trouvées dans la base: {tables}")
            return True
    except Exception as e:
        print("✗ Impossible de lister les tables:")
        print(f"  Erreur: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Test de connexion à la base de données MySQL")
    print("=" * 60)
    print()

    success_count = 0

    if test_engine_connect():
        success_count += 1
    print()

    if test_session_connect():
        success_count += 1
    print()

    if test_database_tables():
        success_count += 1
    print()

    print("=" * 60)
    if success_count == 3:
        print("✓ Tous les tests ont réussi!")
    else:
        print(f"✗ {3 - success_count} test(s) ont échoué")
        print("\nVérifiez que:")
        print("  1. Le container Docker MySQL est démarré")
        print("  2. Les identifiants sont corrects (sp500_main/sp500_main)")
        print("  3. Le port 3306 est accessible")
        print("  4. pymysql est installé: pip install pymysql")
    print("=" * 60)