"""
ml/predictor.py
---------------
Charge le modèle PatchTST + les scalers une seule fois au démarrage (singleton).

Stratégie de prédiction :
  - Ticker connu (scaler dédié)  → normalisation avec le scaler entraîné  (plus précis)
  - Ticker inconnu               → normalisation à la volée sur la fenêtre (fallback)
"""

import os
import json
import pickle
import logging
from typing import List

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
from transformers import PatchTSTForPrediction

logger = logging.getLogger(__name__)

MODEL_DIR = os.getenv("PATCHTST_MODEL_DIR", "./ml/patchtst_saved")

# ── Singleton ───────────────────────────────────────────────────────────────
_model   = None
_scalers = None   # dict[ticker, StandardScaler]  — peut être vide si pas de scalers.pkl
_cfg     = None
_device  = None


def _load():
    """Charge modèle + scalers en mémoire. Appelé une seule fois."""
    global _model, _scalers, _cfg, _device

    if _model is not None:
        return

    logger.info("Chargement du modèle PatchTST depuis %s …", MODEL_DIR)

    # ── Config ────────────────────────────────────────────────────────────
    cfg_path = os.path.join(MODEL_DIR, "inference_config.json")
    with open(cfg_path) as f:
        _cfg = json.load(f)

    # ── Scalers (optionnel) ───────────────────────────────────────────────
    scaler_path = os.path.join(MODEL_DIR, "scalers.pkl")
    if os.path.exists(scaler_path):
        with open(scaler_path, "rb") as f:
            _scalers = pickle.load(f)
        logger.info("Scalers chargés : %d actifs connus", len(_scalers))
    else:
        _scalers = {}
        logger.warning("scalers.pkl introuvable — mode fallback uniquement.")

    # ── Modèle ────────────────────────────────────────────────────────────
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _model = PatchTSTForPrediction.from_pretrained(
        MODEL_DIR,
        num_input_channels=_cfg["num_input_channels"],
        context_length=_cfg["context_length"],
        prediction_length=_cfg["prediction_length"],
        ignore_mismatched_sizes=True,
    )
    _model.to(_device)
    _model.eval()

    logger.info(
        "Modèle prêt sur %s — context=%d  prediction=%d  actifs avec scaler=%d",
        _device,
        _cfg["context_length"],
        _cfg["prediction_length"],
        len(_scalers),
    )


def load_model():
    """À appeler au démarrage de l'app (lifespan FastAPI) pour pré-charger le modèle."""
    _load()


def get_config() -> dict:
    _load()
    return _cfg


def known_tickers() -> list:
    """Retourne les tickers qui ont un scaler dédié (entraînés explicitement)."""
    _load()
    return list(_scalers.keys())


# ── Inférence interne ───────────────────────────────────────────────────────

def _run_inference(scaled: np.ndarray) -> np.ndarray:
    """
    Envoie une fenêtre normalisée au modèle et retourne la sortie normalisée.

    Parameters
    ----------
    scaled : np.ndarray  shape (context_length, 1)

    Returns
    -------
    np.ndarray  shape (prediction_length, 1)
    """
    tensor = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0).to(_device)  # (1, ctx, 1)
    with torch.no_grad():
        output = _model(past_values=tensor).prediction_outputs  # (1, pred_len, 1)
    return output.squeeze(0).cpu().numpy()  # (pred_len, 1)


def _predict_with_scaler(scaler: StandardScaler, close_values: List[float]) -> List[float]:
    """Prédit en utilisant un scaler dédié (actif connu)."""
    ctx_len = _cfg["context_length"]
    raw     = np.array(close_values[-ctx_len:], dtype=np.float32).reshape(-1, 1)
    scaled  = scaler.transform(raw)
    pred    = _run_inference(scaled)
    return scaler.inverse_transform(pred).squeeze().tolist()


def _predict_fallback(close_values: List[float]) -> List[float]:
    """
    Prédit en normalisant à la volée sur la fenêtre reçue (actif inconnu).
    Moins précis qu'un scaler dédié mais fonctionne sur tous les actifs.
    """
    ctx_len = _cfg["context_length"]
    raw     = np.array(close_values[-ctx_len:], dtype=np.float32).reshape(-1, 1)
    scaler  = StandardScaler()
    scaled  = scaler.fit_transform(raw)
    pred    = _run_inference(scaled)
    return scaler.inverse_transform(pred).squeeze().tolist()


# ── Point d'entrée public ───────────────────────────────────────────────────

def predict(ticker: str, close_values: List[float]) -> dict:
    """
    Prédit les `prediction_length` prochaines valeurs de close.

    Utilise le scaler dédié si le ticker a été entraîné,
    sinon normalise à la volée (fallback).

    Parameters
    ----------
    ticker : str
        Symbole boursier (ex: 'ABT'). Peut être n'importe quel ticker en base.
    close_values : list[float]
        Valeurs `close` brutes (prix réels). Doit contenir au moins context_length points.

    Returns
    -------
    dict avec les clés :
        - predictions : list[float]
        - mode        : "dedicated_scaler" | "fallback"

    Raises
    ------
    ValueError
        Si close_values est trop court.
    """
    _load()

    ctx_len = _cfg["context_length"]

    if len(close_values) < ctx_len:
        raise ValueError(
            f"Pas assez de points : {len(close_values)} reçus, {ctx_len} requis."
        )

    if ticker in _scalers:
        logger.debug("Ticker '%s' : scaler dédié", ticker)
        predictions = _predict_with_scaler(_scalers[ticker], close_values)
        mode = "dedicated_scaler"
    else:
        logger.debug("Ticker '%s' : fallback (normalisation à la volée)", ticker)
        predictions = _predict_fallback(close_values)
        mode = "fallback"

    return {"predictions": predictions, "mode": mode}
