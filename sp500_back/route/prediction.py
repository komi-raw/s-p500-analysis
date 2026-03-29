"""
route/prediction.py  (API back — existant)
------------------------------------------
Délègue l'inférence à l'API ML via HTTP (port 8001).
Plus aucun import torch/transformers ici.
"""
import os
from datetime import datetime, timedelta
from typing import List

import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from database.company_dao import CompanyDAO
from database.price_dao import StockPriceDAO

router = APIRouter(prefix="/api/prediction", tags=["prediction"])

ML_API_URL     = os.getenv("ML_API_URL", "http://localhost:8002")
CONTEXT_LENGTH = int(os.getenv("CONTEXT_LENGTH", 64))


def _validate_ticker(db: Session, code: str) -> str:
    code = code.upper().strip()
    if not CompanyDAO.get_company_by_code(db, code):
        raise HTTPException(status_code=404, detail=f"Ticker '{code}' introuvable.")
    return code


@router.get("/")
def get_prediction(
    code: str = Query(..., description="Code boursier (ex: ABT, TSLA, MSFT)"),
    steps: int = Query(None, ge=1, le=200, description="Nombre de pas à prédire"),
    db: Session = Depends(get_db),
):
    ticker = _validate_ticker(db, code)

    # 1. Données MySQL
    rows = StockPriceDAO.get_all_prices(db, ticker, limit=CONTEXT_LENGTH)
    if len(rows) < CONTEXT_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Pas assez de données : {len(rows)}/{CONTEXT_LENGTH} points."
        )

    rows       = list(reversed(rows))   # DESC → ASC
    close_vals = [float(r.close) for r in rows]
    last_date  = rows[-1].date

    # 2. Appel API ML
    try:
        payload: dict = {"ticker": ticker, "close_values": close_vals}
        if steps is not None:
            payload["steps"] = steps
        resp = httpx.post(
            f"{ML_API_URL}/predict/",
            json=payload,
            timeout=60.0,
        )
        resp.raise_for_status()
        ml = resp.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"API ML inaccessible ({ML_API_URL}). Démarrez-la sur le port 8001."
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="API ML : timeout.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Erreur API ML : {e.response.text}")

    # 3. Timestamps estimés — 1 jour par step (indépendant de la granularité des données)
    try:
        last_dt = last_date if isinstance(last_date, datetime) else datetime.fromisoformat(str(last_date))
    except Exception:
        last_dt = None

    steps = []
    for i, val in enumerate(ml["predictions"], start=1):
        step = {"step": i, "predicted_close": round(val, 4)}
        if last_dt:
            step["estimated_date"] = (last_dt + timedelta(days=i)).strftime("%d/%m/%Y")
        steps.append(step)

    return {
        "ticker":            ticker,
        "prediction_mode":   ml["mode"],
        "context_length":    CONTEXT_LENGTH,
        "prediction_length": len(steps),
        "last_known_close":  round(close_vals[-1], 4),
        "last_known_date":   str(last_date),
        "predictions":       steps,
    }


@router.get("/health")
def ml_health():
    """Vérifie que l'API ML est joignable depuis le back."""
    try:
        r = httpx.get(f"{ML_API_URL}/health", timeout=5.0)
        r.raise_for_status()
        return {"ml_api": "ok", "url": ML_API_URL}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
