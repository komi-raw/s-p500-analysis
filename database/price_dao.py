"""
Data Access Object (DAO) pour accéder aux données de la base S&P 500.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from models import CompanyData, get_stock_model

class StockPriceDAO:
    """DAO pour les tables de prix d'actions (dynamiques)."""

    @staticmethod
    def get_all_prices(db: Session, symbol: str, limit: Optional[int] = None, offset: int = 0) -> List[Any]:
        """
        Récupère tous les prix d'un symbole boursier.

        Args:
            db: Session de base de données
            symbol: Symbole boursier (ex: 'AAPL')
            limit: Nombre maximum d'enregistrements
            offset: Décalage pour la pagination

        Returns:
            Liste d'objets de prix
        """
        StockModel = get_stock_model(symbol)
        query = db.query(StockModel).order_by(StockModel.date.desc()).offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_prices_by_date_range(
        db: Session,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None
    ) -> List[Any]:
        """
        Récupère les prix d'un symbole dans une plage de dates.

        Args:
            db: Session de base de données
            symbol: Symbole boursier
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre maximum d'enregistrements

        Returns:
            Liste d'objets de prix
        """
        StockModel = get_stock_model(symbol)
        query = db.query(StockModel).filter(
            and_(
                StockModel.date >= start_date,
                StockModel.date <= end_date
            )
        ).order_by(StockModel.date.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_latest_price(db: Session, symbol: str) -> Optional[Any]:
        """
        Récupère le prix le plus récent d'un symbole.

        Args:
            db: Session de base de données
            symbol: Symbole boursier

        Returns:
            Objet de prix le plus récent ou None
        """
        StockModel = get_stock_model(symbol)
        return db.query(StockModel).order_by(StockModel.date.desc()).first()

    @staticmethod
    def get_prices_by_company_id(
        db: Session,
        symbol: str,
        company_id: int,
        limit: Optional[int] = None
    ) -> List[Any]:
        """
        Récupère les prix pour un company_id spécifique.

        Args:
            db: Session de base de données
            symbol: Symbole boursier
            company_id: ID de l'entreprise
            limit: Nombre maximum d'enregistrements

        Returns:
            Liste d'objets de prix
        """
        StockModel = get_stock_model(symbol)
        query = db.query(StockModel).filter(
            StockModel.companyId == company_id
        ).order_by(StockModel.date.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_total_count(db: Session, symbol: str) -> int:
        """
        Compte le nombre total d'enregistrements pour un symbole.

        Args:
            db: Session de base de données
            symbol: Symbole boursier

        Returns:
            Nombre total d'enregistrements
        """
        StockModel = get_stock_model(symbol)
        return db.query(StockModel).count()

    @staticmethod
    def get_price_statistics(db: Session, symbol: str, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Calcule des statistiques sur les prix (min, max, moyenne).

        Args:
            db: Session de base de données
            symbol: Symbole boursier
            start_date: Date de début (optionnelle)

        Returns:
            Dictionnaire contenant les statistiques
        """
        StockModel = get_stock_model(symbol)

        query = db.query(
            func.min(StockModel.low).label('min_price'),
            func.max(StockModel.high).label('max_price'),
            func.avg(StockModel.close).label('avg_close'),
            func.sum(StockModel.volume).label('total_volume'),
            func.count(StockModel.date).label('count')
        )

        if start_date:
            query = query.filter(StockModel.date >= start_date)

        result = query.first()

        return {
            'symbol': symbol,
            'min_price': float(result.min_price) if result.min_price else None,
            'max_price': float(result.max_price) if result.max_price else None,
            'avg_close': float(result.avg_close) if result.avg_close else None,
            'total_volume': int(result.total_volume) if result.total_volume else 0,
            'count': int(result.count) if result.count else 0
        }

    @staticmethod
    def get_prices_to_dict(db: Session, symbol: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Récupère les prix et les convertit en dictionnaires.

        Args:
            db: Session de base de données
            symbol: Symbole boursier
            limit: Nombre maximum d'enregistrements

        Returns:
            Liste de dictionnaires
        """
        prices = StockPriceDAO.get_all_prices(db, symbol, limit)
        return [price.to_dict() for price in prices]

    @staticmethod
    def get_daily_prices(
        db: Session,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Any]:
        """
        Récupère les prix quotidiens (un prix par jour, typiquement celui de fermeture).

        Args:
            db: Session de base de données
            symbol: Symbole boursier
            start_date: Date de début
            end_date: Date de fin

        Returns:
            Liste d'objets de prix
        """
        StockModel = get_stock_model(symbol)

        # Récupère le dernier prix de chaque jour
        return db.query(StockModel).filter(
            and_(
                StockModel.date >= start_date,
                StockModel.date <= end_date
            )
        ).order_by(StockModel.date.desc()).all()
