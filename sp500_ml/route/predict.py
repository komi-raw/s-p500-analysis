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
    steps: int = Field(default=None, ge=1, le=200, description="Nombre de pas à prédire (défaut : prediction_length du modèle)")


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
    Si steps > prediction_length du modèle, effectue des passes en cascade
    en réinjectant les prédictions comme nouveau contexte.
    """
    cfg = get_config()
    model_pred_len = cfg["prediction_length"]
    target_steps = body.steps if body.steps is not None else model_pred_len

    try:
        context = list(body.close_values)
        all_predictions: List[float] = []
        mode = "fallback"

        while len(all_predictions) < target_steps:
            result = predict(body.ticker, context)
            mode = result["mode"]
            batch = result["predictions"]
            remaining = target_steps - len(all_predictions)
            all_predictions.extend(batch[:remaining])
            context = context[len(batch):] + batch

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur inférence : {e}")

    return PredictResponse(
        ticker=body.ticker,
        mode=mode,
        context_length=cfg["context_length"],
        prediction_length=len(all_predictions),
        predictions=all_predictions,
    )
