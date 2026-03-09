from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from route.prices import router as prices
from route.companies import router as companies

app = FastAPI(
        title="SP500 Analysis API",
        description="API for SP500 data analysis and visualization",
        version="1.0.0",
)

# CORS middleware pour permettre les appels depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices)
app.include_router(companies)


@app.get("/")
def read_root():
    return {"message": "Welcome to the SP500 Analysis API!"}

