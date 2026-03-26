#!/usr/bin/env python3
"""Script de test pour récupérer les données des modèles SQLAlchemy."""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from database_connect import SessionLocal, engine

# Import depuis le dossier sqlalchemy local (pas le module sqlalchemy)
sys.path.insert(0, str(Path(__file__).parent / 'sqlalchemy'))
from models import CompanyData, get_stock_model


def test_get_companies(limit=100):
    """Récupère les premières entreprises de la table company_data."""
    print(f"\n{'='*70}")
    print(f"TEST: Récupération des {limit} premières entreprises")
    print(f"{'='*70}")

    db = SessionLocal()
    try:
        companies = db.query(CompanyData).limit(limit).all()

        if not companies:
            print("⚠️  Aucune entreprise trouvée dans la base de données")
            return []

        print(f"✓ {len(companies)} entreprise(s) récupérée(s)\n")

        # Afficher les 10 premières
        for i, company in enumerate(companies[:10], 1):
            print(f"{i}. Code: {company.code:8} | Nom: {company.name}")

        if len(companies) > 10:
            print(f"... et {len(companies) - 10} autre(s)")

        return companies

    except Exception as e:
        print(f"✗ Erreur lors de la récupération des entreprises: {e}")
        return []
    finally:
        db.close()


def test_get_stock_prices(symbol='AAPL', limit=100):
    """Récupère les premières données de prix pour un symbole boursier."""
    print(f"\n{'='*70}")
    print(f"TEST: Récupération des {limit} premières données pour {symbol}")
    print(f"{'='*70}")

    db = SessionLocal()
    try:
        # Obtenir le modèle dynamique pour ce symbole
        StockModel = get_stock_model(symbol)

        # Récupérer les données triées par date
        prices = db.query(StockModel).order_by(StockModel.date.desc()).limit(limit).all()

        if not prices:
            print(f"⚠️  Aucune donnée trouvée pour {symbol}")
            return []

        print(f"✓ {len(prices)} enregistrement(s) récupéré(s)\n")

        # Afficher les 10 premiers
        print(f"{'Date':<20} | {'Open':>10} | {'High':>10} | {'Low':>10} | {'Close':>10} | {'Volume':>15}")
        print(f"{'-'*20}+{'-'*12}+{'-'*12}+{'-'*12}+{'-'*12}+{'-'*17}")

        for price in prices[:10]:
            date_str = price.date.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{date_str:<20} | {float(price.open):>10.2f} | {float(price.high):>10.2f} | "
                  f"{float(price.low):>10.2f} | {float(price.close):>10.2f} | {price.volume:>15,}")

        if len(prices) > 10:
            print(f"... et {len(prices) - 10} autre(s)")

        # Test de conversion en dictionnaire
        print(f"\n📋 Exemple de conversion en dictionnaire (premier élément):")
        if prices:
            print(prices[0].to_dict())

        return prices

    except Exception as e:
        print(f"✗ Erreur lors de la récupération des données pour {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        db.close()


def test_multiple_symbols(symbols=['AAPL', 'A', 'GOOGL'], limit=10):
    """Test la récupération de données pour plusieurs symboles."""
    print(f"\n{'='*70}")
    print(f"TEST: Récupération de données pour plusieurs symboles")
    print(f"{'='*70}")

    results = {}
    db = SessionLocal()

    try:
        for symbol in symbols:
            try:
                StockModel = get_stock_model(symbol)
                count = db.query(StockModel).count()
                latest = db.query(StockModel).order_by(StockModel.date.desc()).limit(limit).all()

                results[symbol] = {
                    'total': count,
                    'latest': latest
                }

                print(f"\n{symbol}:")
                print(f"  ✓ Total d'enregistrements: {count}")
                print(f"  ✓ Dernières données récupérées: {len(latest)}")
                if latest:
                    print(f"  ✓ Date la plus récente: {latest[0].date}")
                    print(f"  ✓ Dernier prix de clôture: ${float(latest[0].close):.2f}")

            except Exception as e:
                print(f"\n{symbol}:")
                print(f"  ✗ Erreur: {e}")
                results[symbol] = None

        return results

    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTS DES MODÈLES SQLALCHEMY - S&P 500")
    print("="*70)

    # Test 1: Récupérer les entreprises
    companies = test_get_companies(limit=100)

    # Test 2: Récupérer les prix AAPL
    if companies:
        # Utiliser le premier code d'entreprise trouvé, ou AAPL par défaut
        test_symbol = 'AAPL'
        for company in companies:
            if company.code in ['AAPL', 'A', 'GOOGL', 'MSFT']:
                test_symbol = company.code
                break

        aapl_prices = test_get_stock_prices(symbol=test_symbol, limit=100)
    else:
        # Essayer quand même avec AAPL
        aapl_prices = test_get_stock_prices(symbol='AAPL', limit=100)

    # Test 3: Test multiple symboles
    test_multiple_symbols(symbols=['AAPL', 'A', 'MSFT'], limit=5)

    print(f"\n{'='*70}")
    print("✓ Tests terminés!")
    print(f"{'='*70}\n")
