"""
route/backtest.py
-----------------
Backtest : on masque les N derniers steps connus, on lance la prédiction ML
sur le contexte précédent, puis on compare les valeurs prédites aux valeurs réelles.

Granularités supportées :
  - day   : 1 step = 1 jour   (agrégation des rows intraday par date)
  - 15min : 1 step = 15 min   (rows bruts)
  - 30min : 1 step = 30 min   (1 row sur 2 pris depuis les rows 15min)
"""
import math
import os
from datetime import datetime
from collections import OrderedDict

import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from database.company_dao import CompanyDAO
from database.price_dao import StockPriceDAO

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

ML_API_URL     = os.getenv("ML_API_URL", "http://localhost:8002")
CONTEXT_LENGTH = int(os.getenv("CONTEXT_LENGTH", 64))


def _validate_ticker(db: Session, code: str) -> str:
    code = code.upper().strip()
    if not CompanyDAO.get_company_by_code(db, code):
        raise HTTPException(status_code=404, detail=f"Ticker '{code}' introuvable.")
    return code


def _aggregate_daily(rows: list) -> list:
    """Regroupe les rows intraday par jour (date seule) — garde le dernier close."""
    by_day: OrderedDict = OrderedDict()
    for r in rows:
        day = str(r.date)[:10]   # "YYYY-MM-DD"
        by_day[day] = r          # écrase → on garde le dernier de la journée
    return list(by_day.values())


def _aggregate_30min(rows: list) -> list:
    """Rééchantillonne 15min → 30min : 1 row gardé sur 2."""
    return rows[::2]


@router.get("/")
def run_backtest(
    code:        str = Query(...,    description="Code boursier (ex: MSFT)"),
    steps:       int = Query(10, ge=1, le=500, description="Nombre de steps à tester"),
    granularity: str = Query("day",  description="Granularité : day | 15min | 30min"),
    db: Session = Depends(get_db),
):
    """
    Simule une prédiction ML faite `steps` steps avant la fin des données,
    puis compare les prédictions aux vraies valeurs.
    """
    if granularity not in ("day", "15min", "30min"):
        raise HTTPException(status_code=400, detail="granularity doit être : day | 15min | 30min")

    ticker = _validate_ticker(db, code)

    # ── Chargement brut ────────────────────────────────────────────────────────
    # day   : on prend tout (agrégation réduit fortement le volume)
    # 30min : 2× plus de rows que nécessaire (1 row sur 2 gardé)
    # 15min : exactement ce dont on a besoin
    if granularity == "day":
        fetch_limit = None                              # tout récupérer
    elif granularity == "30min":
        fetch_limit = (CONTEXT_LENGTH + steps) * 2 + 50
    else:
        fetch_limit = CONTEXT_LENGTH + steps + 10

    raw_rows = StockPriceDAO.get_all_prices(db, ticker, limit=fetch_limit)
    raw_rows = list(reversed(raw_rows))   # ASC

    # ── Agrégation selon la granularité ──────────────────────────────────────
    if granularity == "day":
        agg_rows = _aggregate_daily(raw_rows)
    elif granularity == "30min":
        agg_rows = _aggregate_30min(raw_rows)
    else:
        agg_rows = raw_rows

    ctx_len = CONTEXT_LENGTH

    needed = ctx_len + steps
    if len(agg_rows) < needed:
        raise HTTPException(
            status_code=422,
            detail=f"Pas assez de données après agrégation '{granularity}' : "
                   f"{len(agg_rows)} disponibles, {needed} requis "
                   f"({ctx_len} contexte + {steps} steps de test)."
        )

    context_rows = agg_rows[:ctx_len]
    actual_rows  = agg_rows[ctx_len:ctx_len + steps]
    close_vals   = [float(r.close) for r in context_rows]

    # ── Appel ML ─────────────────────────────────────────────────────────────
    try:
        resp = httpx.post(
            f"{ML_API_URL}/predict/",
            json={"ticker": ticker, "close_values": close_vals, "steps": steps},
            timeout=60.0,
        )
        resp.raise_for_status()
        ml = resp.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"API ML inaccessible ({ML_API_URL}).")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="API ML : timeout.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Erreur API ML : {e.response.text}")

    predictions = ml["predictions"][:steps]

    # ── Comparaison step par step ─────────────────────────────────────────────
    result_steps = []
    for i, (pred_val, actual_row) in enumerate(zip(predictions, actual_rows), start=1):
        actual_val = float(actual_row.close)
        error      = pred_val - actual_val
        abs_error  = abs(error)
        pct_error  = (abs_error / actual_val * 100) if actual_val else 0.0
        result_steps.append({
            "step":      i,
            "date":      str(actual_row.date),
            "predicted": round(pred_val, 4),
            "actual":    round(actual_val, 4),
            "error":     round(error, 4),
            "abs_error": round(abs_error, 4),
            "pct_error": round(pct_error, 4),
        })

    # ── Métriques globales ────────────────────────────────────────────────────
    n    = len(result_steps)
    mae  = sum(s["abs_error"] for s in result_steps) / n
    rmse = math.sqrt(sum(s["error"] ** 2 for s in result_steps) / n)
    mape = sum(s["pct_error"] for s in result_steps) / n

    return {
        "ticker":            ticker,
        "granularity":       granularity,
        "prediction_mode":   ml.get("mode", "unknown"),
        "context_length":    ctx_len,
        "test_steps":        n,
        "context_end_date":  str(context_rows[-1].date),
        "context_end_close": round(close_vals[-1], 4),
        "metrics": {
            "mae":  round(mae, 4),
            "rmse": round(rmse, 4),
            "mape": round(mape, 4),
        },
        "steps": result_steps,
    }
