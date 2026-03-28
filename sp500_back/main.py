from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from route.prices import router as prices
from route.companies import router as companies
from route.globale import router as globale
from route.prediction import router as prediction
app = FastAPI(
        title="SP500 Analysis API",
        description="API for SP500 data analysis and visualization",
        version="1.0.0",
)

# CORS middleware pour permettre les appels depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices)
app.include_router(companies)
app.include_router(globale)
app.include_router(prediction) 

@app.get("/")
def read_root():
    return {"message": "Welcome to the SP500 Analysis API!"}

