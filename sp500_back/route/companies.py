from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from database.company_dao import CompanyDAO

router = APIRouter(prefix="/api/company", tags=["companies"])


def company_to_id_dict(company):
    """Format attendu par le front : {id, code}."""
    return {
        "id": company.companyIdx,
        "code": company.code,
    }


def company_to_full_dict(company):
    """Format complet avec toutes les infos."""
    return {
        "id": company.companyIdx,
        "code": company.code,
        "name": company.name,
    }


@router.get("/list")
def get_company_list(limit: int = Query(None, description="Nombre max de résultats"),
                     offset: int = Query(0, description="Offset pour pagination"),
                     db: Session = Depends(get_db)):
    """Récupère la liste de toutes les entreprises (id + code)."""
    companies = CompanyDAO.get_all_companies(db, limit=limit, offset=offset)
    return [company_to_id_dict(c) for c in companies]


@router.get("/info")
def get_company_info(code: str = Query(..., description="Code boursier de l'entreprise"),
                     db: Session = Depends(get_db)):
    """Récupère les infos d'une entreprise par son code boursier."""
    company = CompanyDAO.get_company_by_code(db, code.upper())
    if company:
        return company_to_full_dict(company)
    raise HTTPException(status_code=404, detail=f"Company with code '{code}' not found")


@router.get("/search")
def search_companies(query: str = Query(..., description="Terme de recherche"),
                     limit: int = Query(50, description="Nombre max de résultats"),
                     db: Session = Depends(get_db)):
    """Recherche d'entreprises par nom ou code."""
    companies = CompanyDAO.search_companies(db, search_term=query, limit=limit)
    return [company_to_full_dict(c) for c in companies]


@router.get("/count")
def get_companies_count(db: Session = Depends(get_db)):
    """Retourne le nombre total d'entreprises."""
    count = CompanyDAO.get_total_count(db)
    return {"count": count}


