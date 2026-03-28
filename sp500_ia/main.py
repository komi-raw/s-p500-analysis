from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOCAL_DB_URL = "http://localhost:8000/db/query"
client = Groq(api_key="SET_GROQ_API_KEY")

@app.post("/ask/companyinfo/data")
async def chat(req: Request):
    prompt = await req.json()
    try:
        user_prompt = prompt["prompt"]
        import json
        import re
        data_match = re.search(r'informations boursières sur l\'entreprise : (\[.*?\])', user_prompt, re.DOTALL)
        if data_match:
            try:
                data = json.loads(data_match.group(1))
                data = data[-50:]
                user_prompt = user_prompt.replace(data_match.group(1), json.dumps(data))
            except:
                pass
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """Tu es un assistant financier expert en analyse boursière du S&P500. 
Tu réponds en français de manière précise et concise.
Quand on te donne des données boursières (open, high, low, close, volume, date), tu les analyses correctement :
- 'close' = prix de clôture
- 'open' = prix d'ouverture  
- 'high' = prix le plus haut de la journée
- 'low' = prix le plus bas de la journée
- 'volume' = nombre d'actions échangées
Réponds directement et précisément à la question posée."""
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask/ia/sqlproxy")
async def sql_proxy(req: Request):
    prompt = await req.json()
    try:
        sql_prompt = "Génère uniquement une requête SQL sans explication ni backticks pour une base MySQL dont les tables sont nommées par symbole boursier S&P500 (ex: AAPL, TSLA...) avec colonnes: companyId INT, date DATETIME, open DECIMAL, low DECIMAL, high DECIMAL, close DECIMAL, volume BIGINT. Prompt: " + prompt["prompt"]
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": sql_prompt}]
        )
        sql_query = response.choices[0].message.content.replace("```sql", "").replace("```", "").strip()
        db_response = requests.post(LOCAL_DB_URL, json={"query": sql_query})
        db_response.raise_for_status()
        return {"response": db_response.json()["response"]}
    except Exception as e:
        return {"error": str(e)}