from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database.session import get_db
from database.price_dao import StockPriceDAO
from database.company_dao import CompanyDAO


router = APIRouter(prefix="/api/prices", tags=["prices"])


def _validate_company_code(db: Session, code: str) -> str:
    """Vérifie que le code entreprise existe en base."""
    code = code.upper()
    company = CompanyDAO.get_company_by_code(db, code)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with code '{code}' not found")
    return code


@router.get("/{company_code}")
def get_prices(company_code: str,
               start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
               end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
               limit: Optional[int] = Query(None, description="Nombre max de résultats"),
               offset: int = Query(0, description="Offset pour pagination"),
               db: Session = Depends(get_db)):
    """Récupère les prix historiques d'une entreprise par son code boursier."""
    code = _validate_company_code(db, company_code)

    try:
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            prices = StockPriceDAO.get_prices_by_date_range(db, code, start_dt, end_dt, limit=limit)
        else:
            prices = StockPriceDAO.get_all_prices(db, code, limit=limit, offset=offset)

        return [price.to_dict() for price in prices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching prices: {str(e)}")


@router.get("/{company_code}/latest")
def get_latest_price(company_code: str, db: Session = Depends(get_db)):
    """Récupère le dernier prix disponible d'une entreprise."""
    code = _validate_company_code(db, company_code)

    price = StockPriceDAO.get_latest_price(db, code)
    if price:
        return price.to_dict()
    raise HTTPException(status_code=404, detail=f"No price data found for '{code}'")


@router.get("/{company_code}/statistics")
def get_price_statistics(company_code: str,
                         start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
                         db: Session = Depends(get_db)):
    """Récupère les statistiques de prix d'une entreprise."""
    code = _validate_company_code(db, company_code)

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        stats = StockPriceDAO.get_price_statistics(db, code, start_date=start_dt)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


@router.get("/{company_code}/count")
def get_price_count(company_code: str, db: Session = Depends(get_db)):
    """Retourne le nombre total d'enregistrements de prix pour une entreprise."""
    code = _validate_company_code(db, company_code)

    count = StockPriceDAO.get_total_count(db, code)
    return {"code": code, "count": count}
