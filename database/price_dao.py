from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from decimal import Decimal
from datetime import datetime
from models import PriceBase  # ton modèle

class PriceDAO:
    """
    DAO pour accéder aux données de prix.
    """

    @staticmethod
    def get_all_by_company(session: Session, company_id: int) -> List[PriceBase]:
        """
        Récupère tous les prix d'une entreprise par son ID, triés par date croissante.
        """
        stmt = select(PriceBase).where(PriceBase.companyId == company_id).order_by(PriceBase.date.asc())
        result = session.execute(stmt)
        return result.scalars().all()
