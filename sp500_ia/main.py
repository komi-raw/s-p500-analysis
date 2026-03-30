from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOCAL_DB_URL = "http://localhost:8000/db/query"
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

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
        tables_disponibles = ["AOS", "APD", "AVY", "AZO", "BALL", "BKNG", "BSX", "CARR", "CDNS", "CDW", "CFG", "CHD", "CHRW", "CHTR", "CI", "CL", "CLX", "CMCSA", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COIN", "COO", "COP", "COR", "COST", "CPAY", "CPB", "CPRT", "CPT", "CRL", "CRM", "CSCO", "CSGP", "CSX", "CTAS", "CTRA", "CTSH", "CTVA", "CVS", "CVX", "D", "DAL", "DASH", "DAY", "DD", "DDOG", "DE", "DECK", "DELL", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR", "DOC", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EG", "EIX", "EL", "ELV", "EME", "EMN", "EMR", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ERIE", "ES", "ESS", "ETN", "ETR", "EVRG", "EW", "EXC", "EXE", "EXPD", "EXPE", "EXR", "F", "FANG", "FCX", "FDS", "FDX", "FE", "FFIV", "FI", "FICO", "FIS", "FITB", "FOX", "FOXA", "FRT", "FSLR", "FTNT", "FTV", "GD", "GDDY", "GE", "GEHC", "GEN", "GEV", "GILD", "GIS", "GL", "GLW", "GM", "GNRC", "GOOGL", "GPC", "GPN", "GRMN", "GS", "GWW", "HAL", "HAS", "HBAN", "HCA", "HD", "HIG", "HII", "HLT", "HOLX", "HON", "HOOD", "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUBB", "HUM", "HWM", "IBKR", "IBM", "ICE", "IDXX", "IEX", "IFF", "INCY", "INTC", "INTU", "INVH", "IP", "IPG", "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT", "JBL", "JCI", "JKHY", "JNJ", "JPM", "K", "KDP", "KHC", "KIM", "KKR", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH", "LHX", "LII", "LIN", "LKQ", "LLY", "LMT", "LNT", "LOW", "LRCX", "LULU", "LUV", "LVS", "LW", "LYB", "LYV", "MA", "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "MGM", "MHK", "MKC", "MLM", "MMC", "MMM", "MNST", "MO", "MOH", "MOS", "MPC", "MPWR", "MRK", "MRNA", "MS", "MSCI", "MSFT", "MSI", "MTB", "MTCH", "MTD", "MU", "NCLH", "NDAQ", "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWS", "NWSA", "NXPI", "O", "ODFL", "OKE", "OMC", "ORCL", "ORLY", "OTIS", "OXY", "PANW", "PAYC", "PAYX", "PCAR", "PCG", "PEG", "PEP", "PFE", "PFG", "PGR", "PH", "PHM", "PKG", "PLD", "PLTR", "PM", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSKY", "PSX", "PTC", "PWR", "PYPL", "RCL", "REG", "REGN", "RF", "RJF", "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "RVTY", "SBAC", "SCHW", "SHW", "SJM", "SLB", "SMCI", "SNA", "SNPS", "SO", "SOLV", "SPG", "SPGI", "SRE", "STE", "STLD", "STT", "STX", "STZ", "SW", "SWK", "SWKS", "SYF", "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH", "TER", "TFC", "TGT", "TJX", "TKO", "TMO", "TMUS", "TPL", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TTD", "TTWO", "TXN", "TXT", "TYL", "UAL", "UBER", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB"]

        sql_prompt = f"""Tu es un générateur de requêtes SQL pour une base MySQL.
        Les tables disponibles sont UNIQUEMENT : {', '.join(tables_disponibles)}
        N'utilise PAS d'autres tables que celles listées ci-dessus.
        Chaque table a ces colonnes : companyId INT, date DATETIME, open DECIMAL, low DECIMAL, high DECIMAL, close DECIMAL, volume BIGINT.
        RÈGLES STRICTES :
        - Réponds UNIQUEMENT avec la requête SQL, rien d'autre
        - Pas de backticks, pas d'explication, pas de commentaires
        - Utilise LIMIT 100 maximum
        - La requête doit être valide MySQL
        - N'utilise QUE les tables listées ci-dessus
        Question : """ + prompt["prompt"]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": sql_prompt}]
        )
        
        sql_query = response.choices[0].message.content
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        if not any(keyword in sql_query.upper() for keyword in ["SELECT", "SHOW", "DESCRIBE"]):
            return {"error": "Le LLM n'a pas généré une requête SQL valide", "raw": sql_query}
        
        db_response = requests.post(LOCAL_DB_URL, json={"query": sql_query})
        
        if db_response.status_code != 200:
            return {"error": f"Erreur SQL : {db_response.text}", "query": sql_query}
            
        result = db_response.json()
        
        summary_prompt = f"Voici les résultats d'une requête SQL : {str(result)[:2000]}. Résume ces données en français en 3-4 phrases."
        summary = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        
        return {
            "response": summary.choices[0].message.content,
            "query": sql_query,
            "raw_data": result[:10] if isinstance(result, list) else result
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask/ia/sector")
async def sector_analyst(req: Request):
    payload = await req.json()
    try:
        user_prompt = payload.get("prompt", "")

        system_prompt = """Tu es un expert en analyse financière et boursière du S&P500.
Tu réponds en français de manière précise et structurée.
Tu analyses des prédictions ML (PatchTST) par secteur GICS pour identifier :
- Les meilleures dynamiques haussières
- Les tendances sectorielles communes
- Les entreprises sous-performantes
- Des recommandations d'observation à court terme."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}


@app.post("/ask/ia/analyst")
async def analyst(req: Request):
    prompt = await req.json()
    try:
        companies = prompt.get("companies", [])
        user_prompt = prompt.get("prompt", "")

        if len(companies) > 5:
            return {"error": "Maximum 5 entreprises autorisées pour l'analyse IA."}

        companies_data = {}
        for company in companies:
            try:
                res = requests.get(f"http://localhost:8000/api/price/list?code={company}", timeout=10)
                res.raise_for_status()
                data = res.json()
                companies_data[company] = data[:20] if len(data) > 20 else data
            except Exception as e:
                companies_data[company] = {"error": str(e)}

        system_prompt = """Tu es un expert en analyse financière et boursière du S&P500.
Tu réponds en français de manière précise et structurée.
Tu sais :
- Analyser les tendances haussières/baissières
- Comparer plusieurs entreprises entre elles (prix, volume, volatilité)
- Détecter les anomalies : pics de volume inhabituels, variations de prix extrêmes, journées atypiques
- Calculer des indicateurs : moyenne, volatilité, variation en pourcentage
- Identifier les meilleures et pires performances sur une période
Quand tu compares plusieurs entreprises, structure ta réponse avec des sections claires par entreprise.
Quand tu détectes des anomalies, explique pourquoi c'est anormal par rapport aux données habituelles."""

        full_prompt = f"""Entreprises analysées : {', '.join(companies) if companies else 'aucune'}
Nombre d'entreprises : {len(companies)}
Données disponibles : {str(companies_data)}
Question : {user_prompt}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}