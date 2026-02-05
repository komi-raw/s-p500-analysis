"""
Data Access Object (DAO) pour accéder aux données de la base S&P 500.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from models import CompanyData, get_stock_model


class CompanyDAO:
    """DAO pour la table company_data."""

    @staticmethod
    def get_all_companies(db: Session, limit: Optional[int] = None, offset: int = 0) -> List[CompanyData]:
        """
        Récupère toutes les entreprises.

        Args:
            db: Session de base de données
            limit: Nombre maximum d'enregistrements (None = tous)
            offset: Décalage pour la pagination

        Returns:
            Liste d'objets CompanyData
        """
        query = db.query(CompanyData).offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_company_by_id(db: Session, company_idx: int) -> Optional[CompanyData]:
        """
        Récupère une entreprise par son ID.

        Args:
            db: Session de base de données
            company_idx: ID de l'entreprise

        Returns:
            Objet CompanyData ou None
        """
        return db.query(CompanyData).filter(CompanyData.companyIdx == company_idx).first()

    @staticmethod
    def get_company_by_code(db: Session, code: str) -> Optional[CompanyData]:
        """
        Récupère une entreprise par son code boursier.

        Args:
            db: Session de base de données
            code: Code boursier (ex: 'AAPL')

        Returns:
            Objet CompanyData ou None
        """
        return db.query(CompanyData).filter(CompanyData.code == code).first()

    @staticmethod
    def get_companies_by_codes(db: Session, codes: List[str]) -> List[CompanyData]:
        """
        Récupère plusieurs entreprises par leurs codes.

        Args:
            db: Session de base de données
            codes: Liste de codes boursiers

        Returns:
            Liste d'objets CompanyData
        """
        return db.query(CompanyData).filter(CompanyData.code.in_(codes)).all()

    @staticmethod
    def get_total_count(db: Session) -> int:
        """
        Compte le nombre total d'entreprises.

        Args:
            db: Session de base de données

        Returns:
            Nombre total d'entreprises
        """
        return db.query(CompanyData).count()

    @staticmethod
    def search_companies(db: Session, search_term: str, limit: int = 50) -> List[CompanyData]:
        """
        Recherche des entreprises par nom ou code.

        Args:
            db: Session de base de données
            search_term: Terme de recherche
            limit: Nombre maximum de résultats

        Returns:
            Liste d'objets CompanyData
        """
        search_pattern = f"%{search_term}%"
        return db.query(CompanyData).filter(
            or_(
                CompanyData.code.like(search_pattern),
                CompanyData.name.like(search_pattern)
            )
        ).limit(limit).all()
