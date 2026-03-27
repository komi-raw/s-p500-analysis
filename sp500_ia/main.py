from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
LOCAL_DB_URL = "http://localhost:8000/db/query"

class Prompt(BaseModel):
    prompt: str

@app.post("/ask/companyinfo/data")
async def chat(req: Request):
    prompt = await req.json()
    print("received ")
    print(prompt)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "deepseek-r1",
                "prompt": prompt["prompt"],
                "stream": False
            }
        )

        response.raise_for_status()
        data = response.json()

        return {
            "response": data["response"]
        }

    except Exception as e:
        return {
            "error": str(e)
        }

@app.post("/ask/ia/sqlproxy")
async def chat(req: Request):
    prompt = await req.json()
    print("received ")
    print(prompt)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "deepseek-r1",
                "prompt": "Tu dois me générer uniquement une requête sql avec une base à des tables qui ont comme nom un nom parmi [  \"TMUS\",  \"LHX\",  \"COO\",  \"WDC\",  \"F\",  \"CRWD\",  \"DE\",  \"FOX\",  \"BRK.B\",  \"AMAT\",  \"OTIS\",  \"APH\",  \"VLTO\",  \"OXY\",  \"A\",  \"EXR\",  \"PCAR\",  \"QCOM\",  \"ABT\",  \"BK\",  \"HSY\",  \"APTV\",  \"TPR\",  \"MPC\",  \"CNP\",  \"HUM\",  \"TSCO\",  \"AEE\",  \"RJF\",  \"AXP\",  \"AEP\",  \"BAC\",  \"SBUX\",  \"TPL\",  \"KDP\",  \"LLY\",  \"LRCX\",  \"SNPS\",  \"CTRA\",  \"DG\",  \"MCO\",  \"CPB\",  \"CPT\",  \"FRT\",  \"CFG\",  \"ALL\",  \"CPAY\",  \"SLB\",  \"CBRE\",  \"POOL\",  \"DVN\",  \"PEP\",  \"EFX\",  \"CMI\",  \"TJX\",  \"ULTA\",  \"TT\",  \"ODFL\",  \"PSKY\",  \"KR\",  \"BSX\",  \"EQT\",  \"TDG\",  \"CINF\",  \"RL\",  \"ZBRA\",  \"IRM\",  \"JKHY\",  \"MS\",  \"JBL\",  \"CSCO\",  \"TER\",  \"CEG\",  \"HLT\",  \"VTR\",  \"HD\",  \"D\",  \"OMC\",  \"ADI\",  \"GIS\",  \"GRMN\",  \"SOLV\",  \"APP\",  \"ADSK\",  \"RMD\",  \"APA\",  \"AMD\",  \"TMO\",  \"NDSN\",  \"AVY\",  \"HON\",  \"NTRS\",  \"DELL\",  \"KMI\",  \"ON\",  \"STT\",  \"EVRG\",  \"NDAQ\",  \"PNR\",  \"PH\",  \"USB\",  \"CSX\",  \"PODD\",  \"MO\",  \"RTX\",  \"AXON\",  \"VZ\",  \"IBKR\",  \"WBD\",  \"EA\",  \"IQV\",  \"SYY\",  \"HUBB\",  \"NVR\",  \"HWM\",  \"IFF\",  \"HST\",  \"JPM\",  \"MU\",  \"FDX\",  \"MTCH\",  \"WM\",  \"T\",  \"TXT\",  \"DLR\",  \"SO\",  \"CAH\",  \"MTB\",  \"LDOS\",  \"IT\",  \"VTRS\",  \"TRMB\",  \"BLDR\",  \"EL\",  \"COP\",  \"TEL\",  \"SWK\",  \"VST\",  \"WST\",  \"NXPI\",  \"WFC\",  \"DRI\",  \"KEY\",  \"DD\",  \"INCY\",  \"ZTS\",  \"IPG\",  \"WEC\",  \"EXE\",  \"XEL\",  \"TSN\",  \"TRGP\",  \"IR\",  \"AFL\",  \"LULU\",  \"TAP\",  \"CRL\",  \"INTC\",  \"MDLZ\",  \"BALL\",  \"NUE\",  \"DOW\",  \"UNP\",  \"TROW\",  \"MSCI\",  \"PPG\",  \"GEHC\",  \"BR\",  \"PANW\",  \"LII\",  \"AKAM\",  \"LYB\",  \"SYK\",  \"ACGL\",  \"CDNS\",  \"CME\",  \"SBAC\",  \"GPN\",  \"PTC\",  \"MAA\",  \"CVX\",  \"EXPE\",  \"WRB\",  \"NVDA\",  \"MSI\",  \"STLD\",  \"CCI\",  \"BBY\",  \"PFG\",  \"KVUE\",  \"MCD\",  \"J\",  \"KLAC\",  \"PSA\",  \"NFLX\",  \"KMX\",  \"SWKS\",  \"COF\",  \"STZ\",  \"LMT\",  \"ROST\",  \"ELV\",  \"ADBE\",  \"AJG\",  \"MMC\",  \"FANG\",  \"VLO\",  \"MTD\",  \"HOLX\",  \"LYV\",  \"FSLR\",  \"ZBH\",  \"STX\",  \"ROP\",  \"CMS\",  \"ALGN\",  \"AIG\",  \"RVTY\",  \"AAPL\",  \"GWW\",  \"DHI\",  \"CHRW\",  \"ISRG\",  \"META\",  \"AIZ\",  \"COST\",  \"K\",  \"DHR\",  \"DECK\",  \"MRK\",  \"TECH\",  \"DOC\",  \"V\",  \"LUV\",  \"CBOE\",  \"AVGO\",  \"GNRC\",  \"MKC\",  \"AWK\",  \"CRM\",  \"PPL\",  \"ABNB\",  \"TYL\",  \"CF\",  \"PYPL\",  \"DTE\",  \"LVS\",  \"HBAN\",  \"CAT\",  \"MRNA\",  \"FTNT\",  \"BMY\",  \"ERIE\",  \"PKG\",  \"LIN\",  \"NI\",  \"KHC\",  \"TSLA\",  \"DAL\",  \"MHK\",  \"PWR\",  \"DPZ\",  \"CSGP\",  \"BA\",  \"AMP\",  \"DDOG\",  \"NWSA\",  \"EME\",  \"ECL\",  \"RF\",  \"BXP\",  \"FDS\",  \"HIG\",  \"CMCSA\",  \"DGX\",  \"NOC\",  \"HAL\",  \"AME\",  \"HCA\",  \"ATO\",  \"CARR\",  \"CCL\",  \"DOV\",  \"PFE\",  \"FI\",  \"NEE\",  \"FFIV\",  \"GM\",  \"PM\",  \"TRV\",  \"AES\",  \"MOH\",  \"CL\",  \"MAR\",  \"DASH\",  \"KMB\",  \"WYNN\",  \"IBM\",  \"CHD\",  \"INVH\",  \"TKO\",  \"ETN\",  \"GLW\",  \"ALLE\",  \"NOW\",  \"INTU\",  \"DAY\",  \"BLK\",  \"VMC\",  \"CB\",  \"TDY\",  \"UHS\",  \"GL\",  \"DVA\",  \"COIN\",  \"BX\",  \"KKR\",  \"VRSK\",  \"ADP\",  \"O\",  \"ED\",  \"NCLH\",  \"FCX\",  \"PG\",  \"KIM\",  \"GDDY\",  \"ADM\",  \"FAST\",  \"FE\",  \"EPAM\",  \"PRU\",  \"TTWO\",  \"MAS\",  \"SMCI\",  \"SJM\",  \"LH\",  \"SCHW\",  \"AON\",  \"WMB\",  \"GEN\",  \"MA\",  \"GOOGL\",  \"APD\",  \"SNA\",  \"SRE\",  \"PNC\",  \"MLM\",  \"MGM\",  \"FOXA\",  \"ORLY\",  \"ROK\",  \"VICI\",  \"GD\",  \"GPC\",  \"YUM\",  \"BKNG\",  \"AMCR\",  \"WTW\",  \"MNST\",  \"GEV\",  \"EG\",  \"IP\",  \"UDR\",  \"RCL\",  \"ACN\",  \"AMGN\",  \"PLD\",  \"HAS\",  \"BIIB\",  \"IDXX\",  \"UAL\",  \"APO\",  \"UPS\",  \"XYL\",  \"UNH\",  \"CLX\",  \"REG\",  \"PSX\",  \"BG\",  \"EQR\",  \"LEN\",  \"PCG\",  \"MSFT\",  \"WY\",  \"MCHP\",  \"VRSN\",  \"KO\",  \"WDAY\",  \"EXPD\",  \"NSC\",  \"C\",  \"PNW\",  \"AVB\",  \"FICO\",  \"URI\",  \"LNT\",  \"EXC\",  \"SYF\",  \"CVS\",  \"HSIC\",  \"PLTR\",  \"NEM\",  \"REGN\",  \"SW\",  \"PHM\",  \"FITB\",  \"VRTX\",  \"TTD\",  \"OKE\",  \"HII\",  \"ALB\",  \"MOS\",  \"EQIX\",  \"BF.B\",  \"SPG\",  \"FTV\",  \"HOOD\",  \"MET\",  \"EIX\",  \"WAT\",  \"WELL\",  \"SHW\",  \"BAX\",  \"ABBV\",  \"GILD\",  \"HRL\",  \"DXCM\",  \"CDW\",  \"IVZ\",  \"CI\",  \"L\",  \"EMR\",  \"CPRT\",  \"CTVA\",  \"LKQ\",  \"HPE\",  \"TGT\",  \"TXN\",  \"COR\",  \"LW\",  \"WMT\",  \"CMG\",  \"EOG\",  \"DLTR\",  \"CHTR\",  \"NRG\",  \"AMT\",  \"ANET\",  \"TFC\",  \"ROL\",  \"ES\",  \"PGR\",  \"AOS\",  \"DUK\",  \"WSM\",  \"ESS\",  \"BEN\",  \"PAYX\",  \"JNJ\",  \"MPWR\",  \"CNC\",  \"NWS\",  \"LOW\",  \"MDT\",  \"UBER\",  \"CTAS\",  \"ORCL\",  \"EMN\",  \"IEX\",  \"BRO\",  \"EW\",  \"BDX\",  \"FIS\",  \"AMZN\",  \"XYZ\",  \"ETR\",  \"NKE\",  \"BKR\",  \"RSG\",  \"MMM\",  \"ITW\",  \"SPGI\",  \"ARE\",  \"GE\",  \"GS\",  \"STE\",  \"XOM\",  \"MCK\",  \"JCI\",  \"PAYC\",  \"HPQ\",  \"CTSH\",  \"NTAP\",  \"DIS\",  \"AZO\",  \"PEG\",  \"CAG\",  \"EBAY\",  \"WAB\",  \"JBHT\",  \"ICE\",  \"KEYS\",  \"BABA\"] et qui représente une entreprise du SP500 avec comme colonnes pour chaque table ( companyId INT NOT NULL, date    DATETIME NOT NULL, open    DECIMAL(10,4) NOT NULL, low     DECIMAL(10,4) NOT NULL, high    DECIMAL(10,4) NOT NULL, close   DECIMAL(10,4) NOT NULL, volume  BIGINT NOT NULL). Génère moi une requête sql correpondant au prompt suivant : " + prompt["prompt"],
                "stream": False
            }
        )

        response.raise_for_status()
        data = response.json()

        data["response"].replace("```sql","")
        data["response"].replace("```","")

        response = requests.post(
            LOCAL_DB_URL,
            json={
                "query": data["response"],
            }
        )

        response.raise_for_status()
        data = response.json()

        return {
            "response": data["response"]
        }

    except Exception as e:
        return {
            "error": str(e)
        }