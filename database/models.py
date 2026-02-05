from sqlalchemy import Column, Integer, String, DateTime, BigInteger, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class CompanyData(Base):
    """Modèle pour la table company_data."""
    __tablename__ = 'company_data'

    companyIdx = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False)
    name = Column(String(100), nullable=True)


    """"""

    def __repr__(self):
        return f"<CompanyData(companyIdx={self.companyIdx}, code='{self.code}', name='{self.name}')>"


def create_stock_price_model(table_name: str):
    """
    Factory function pour créer dynamiquement un modèle SQLAlchemy
    pour une table de prix d'actions spécifique.

    Args:
        table_name: Le nom de la table (ex: 'AAPL', 'A', 'GOOGL', etc.)

    Returns:
        Une classe de modèle SQLAlchemy configurée pour cette table

    Exemple:
        AAPL = create_stock_price_model('AAPL')
        A = create_stock_price_model('A')
    """

    class StockPrice(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        companyId = Column(Integer, nullable=False, primary_key=True)
        date = Column(DateTime, nullable=False, primary_key=True)
        open = Column(DECIMAL(10, 4), nullable=False)
        low = Column(DECIMAL(10, 4), nullable=False)
        high = Column(DECIMAL(10, 4), nullable=False)
        close = Column(DECIMAL(10, 4), nullable=False)
        volume = Column(BigInteger, nullable=False)

        def __repr__(self):
            return (f"<{table_name}(companyId={self.companyId}, date={self.date}, "
                   f"open={self.open}, high={self.high}, low={self.low}, "
                   f"close={self.close}, volume={self.volume})>")

        def to_dict(self):
            """Convertit l'objet en dictionnaire."""
            return {
                'companyId': self.companyId,
                'date': self.date.isoformat() if isinstance(self.date, datetime) else self.date,
                'open': float(self.open) if self.open else None,
                'low': float(self.low) if self.low else None,
                'high': float(self.high) if self.high else None,
                'close': float(self.close) if self.close else None,
                'volume': self.volume
            }

    # Renommer la classe pour refléter le symbole boursier
    StockPrice.__name__ = f"{table_name}StockPrice"
    StockPrice.__qualname__ = f"{table_name}StockPrice"

    return StockPrice


# Cache pour stocker les modèles déjà créés
_stock_models_cache = {}


def get_stock_model(symbol: str):
    """
    Récupère ou crée un modèle de prix d'actions pour un symbole donné.
    Utilise un cache pour éviter de recréer les mêmes modèles.

    Args:
        symbol: Le symbole boursier (ex: 'AAPL', 'A', 'GOOGL')

    Returns:
        Le modèle SQLAlchemy pour ce symbole

    Exemple:
        aapl_model = get_stock_model('AAPL')
        session.query(aapl_model).filter(aapl_model.companyId == 1).all()
    """
    if symbol not in _stock_models_cache:
        _stock_models_cache[symbol] = create_stock_price_model(symbol)
    return _stock_models_cache[symbol]