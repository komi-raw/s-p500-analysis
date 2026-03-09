from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from database.company_dao import CompanyDAO

router = APIRouter(prefix="/api/companies", tags=["companies"])


def company_to_dict(company):
    """Convertit un objet CompanyData en dict propre (sans _sa_instance_state)."""
    return {
        "companyIdx": company.companyIdx,
        "code": company.code,
        "name": company.name,
    }


@router.get("")
def get_companies(limit: int = Query(None, description="Nombre max de résultats"),
                  offset: int = Query(0, description="Offset pour pagination"),
                  db: Session = Depends(get_db)):
    """Récupère la liste de toutes les entreprises."""
    companies = CompanyDAO.get_all_companies(db, limit=limit, offset=offset)
    return [company_to_dict(c) for c in companies]


@router.get("/search")
def search_companies(query: str = Query(..., description="Terme de recherche"),
                     limit: int = Query(50, description="Nombre max de résultats"),
                     db: Session = Depends(get_db)):
    """Recherche d'entreprises par nom ou code."""
    companies = CompanyDAO.search_companies(db, search_term=query, limit=limit)
    return [company_to_dict(c) for c in companies]


@router.get("/count")
def get_companies_count(db: Session = Depends(get_db)):
    """Retourne le nombre total d'entreprises."""
    count = CompanyDAO.get_total_count(db)
    return {"count": count}


@router.get("/{code}")
def get_company_by_code(code: str, db: Session = Depends(get_db)):
    """Récupère une entreprise par son code boursier."""
    company = CompanyDAO.get_company_by_code(db, code.upper())
    if company:
        return company_to_dict(company)
    raise HTTPException(status_code=404, detail=f"Company with code '{code}' not found")

