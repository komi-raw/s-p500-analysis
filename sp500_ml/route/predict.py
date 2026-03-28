"""
route/predict.py
----------------
POST /predict
  Body : { "ticker": "ABT", "close_values": [127.4, 127.6, ...] }
  → { "predictions": [...], "mode": "dedicated_scaler"|"fallback" }
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from ml.predictor import predict, get_config

router = APIRouter(prefix="/predict", tags=["predict"])


class PredictRequest(BaseModel):
    ticker: str = Field(..., description="Symbole boursier (ex: ABT)")
    close_values: List[float] = Field(
        ...,
        description="Valeurs close brutes, au moins context_length points"
    )


class PredictResponse(BaseModel):
    ticker: str
    mode: str                        # "dedicated_scaler" ou "fallback"
    context_length: int
    prediction_length: int
    predictions: List[float]


@router.post("/", response_model=PredictResponse)
def run_prediction(body: PredictRequest):
    """
    Reçoit les close_values depuis l'API back et retourne les prédictions.
    L'API back est responsable de récupérer les données MySQL et de construire
    la liste close_values avant d'appeler cet endpoint.
    """
    cfg = get_config()

    try:
        result = predict(body.ticker, body.close_values)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur inférence : {e}")

    return PredictResponse(
        ticker=body.ticker,
        mode=result["mode"],
        context_length=cfg["context_length"],
        prediction_length=cfg["prediction_length"],
        predictions=result["predictions"],
    )
