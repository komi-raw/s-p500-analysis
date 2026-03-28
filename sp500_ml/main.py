"""
API ML dédiée — PatchTST
Lance sur le port 8001 : uvicorn main:app --port 8001 --reload
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ml.predictor import load_model
from route.predict import router as predict_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Chargement du modèle PatchTST...")
    load_model()
    print("Modèle prêt — API ML opérationnelle.")
    yield


app = FastAPI(
    title="SP500 ML API",
    description="API dédiée à l'inférence PatchTST",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)


@app.get("/health")
def health():
    return {"status": "ok"}
