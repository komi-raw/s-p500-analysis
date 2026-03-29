# S&P 500 Analysis Platform

Plateforme d'analyse financière complète pour les actions du S&P 500, combinant :

- **Visualisation** interactive des données historiques OHLCV (bougies japonaises)
- **Prédictions par deep learning** avec le modèle PatchTST (intraday et quotidien)
- **Analyse en langage naturel** via LLM Groq (llama-3.3-70b-versatile)
- **Exploration sectorielle** GICS avec prédictions ML croisées et synthèse IA
- **Backtesting** — comparaison prédictions ML vs données réelles sur 13 tickers

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│               sp500_front  (Vue 3 + TypeScript · port 5173)      │
│   HomeView · Viewer · AIAnalyst · PredictionView · SectorExplorer│
└─────────┬──────────────────┬────────────────────┬───────────────┘
          │                  │                    │
          ▼                  ▼                    ▼
┌──────────────────┐  ┌────────────────┐  ┌──────────────────────┐
│   sp500_back     │  │   sp500_ml     │  │      sp500_ia        │
│  API principale  │  │   API ML       │  │    API LLM (Groq)    │
│   port 8000      │  │   port 8002    │  │    port 8001         │
└────────┬─────────┘  └──────┬─────────┘  └──────────┬───────────┘
         │                   │                        │
         ▼                   ▼                        ▼
┌──────────────────┐  ┌────────────────┐  ┌──────────────────────┐
│  MySQL · 3306    │  │   PatchTST     │  │  Groq Cloud API      │
│  (Docker)        │  │  (LSTM-free    │  │  llama-3.3-70b       │
│  ~500 tickers    │  │  transformer)  │  │  -versatile          │
└──────────────────┘  └────────────────┘  └──────────────────────┘
```

> `sp500_back` orchestre les appels vers `sp500_ml` et renvoie les prédictions au frontend.
> `sp500_ia` est appelé directement depuis le frontend (analyses LLM).

---

## Services et ports

| Service | Port | Rôle |
|---------|------|------|
| `sp500_front` | 5173 | Interface web Vue 3 + TypeScript + Tailwind CSS |
| `sp500_back` | 8000 | API REST principale (données OHLCV, prédiction, backtest) |
| `sp500_ia` | 8001 | Analyse financière LLM — Groq / llama-3.3-70b |
| `sp500_ml` | 8002 | Prédictions de prix — modèle PatchTST |
| MySQL | 3306 | Base de données (Docker) |

---

## Vues disponibles

### Data Viewer `/data/view`

Graphique en bougies japonaises temps réel (via `lightweight-charts`) pour chaque action du S&P 500.
Sélection du ticker et de la période. Chat IA intégré pour interroger les données OHLCV affichées en langage naturel.

**Fonctionnalités :** zoom, défilement, tooltips OHLCV, analyse IA sur données actuelles.

---

### AI Analyst `/ai/analyst`

Analyse comparative multi-entreprises par intelligence artificielle.

**Deux modes :**

| Mode | Description |
|------|-------------|
| **Chat** | Questions libres : comparaisons, tendances, anomalies, corrélations sectorielles |
| **SQL** | L'IA génère une requête SQL à partir d'une question en langage naturel, l'exécute et interprète le résultat |

**Fonctionnalités :** sélection par checkboxes avec recherche, export `.txt` de la conversation complète.

---

### ML Prediction `/ml/prediction`

Prédictions de prix futurs via le modèle PatchTST.

| Paramètre | Valeurs | Description |
|-----------|---------|-------------|
| Ticker | ex: AAPL, MSFT | Action S&P 500 |
| Granularité | `day`, `hour`, `15min` | Pas de temps des prédictions |
| Steps | 1 – 500 | Nombre de points à prédire |

Affiche un graphique combinant historique réel (noir) et courbe de prédiction (orange), ainsi qu'un tableau des valeurs estimées avec dates.

**Fonctionnalités :** export `.csv` des prédictions (ticker, close estimé, date).

---

### Sector Explorer `/sector/explorer`

Vue sectorielle GICS — prédictions ML en parallèle + synthèse IA croisée.

1. Sélection d'un secteur GICS (11 secteurs disponibles)
2. Cocher les entreprises à analyser
3. Le frontend lance toutes les prédictions ML simultanément (`Promise.allSettled`)
4. Le résumé ML est soumis au LLM pour une interprétation sectorielle globale

**Affichage :** sparklines SVG par ticker (couleur verte/rouge selon la tendance), tableau récapitulatif avec variation % et prédictions.

**Fonctionnalités :** export double — `.csv` (données ML) + `.txt` (analyse IA).

---

## Installation et démarrage

### Prérequis

- Python 3.8+
- Node.js 18+ et npm
- Docker Desktop (ou Docker Engine)
- Clé API Groq ([console.groq.com/keys](https://console.groq.com/keys))

---

### Étape 1 — Préparer la base de données *(une seule fois)*

```bash
./setup.sh          # Linux / macOS / WSL
.\setup.ps1         # Windows (PowerShell)
```

Ce script :
1. Construit l'image Docker MySQL 8.0 personnalisée
2. Crée et démarre le conteneur `my_sp500_db` sur le port `3306`
3. Attend que MySQL soit prêt à accepter les connexions
4. Charge tous les fichiers SQL depuis `SQL_Output/SQL_Output_compiled/SQL_Output/`

> **Si le conteneur existe déjà**, le script propose de le recréer (réponse `o/n`).

---

### Étape 2 — Lancer la plateforme

```bash
./start.sh          # Linux / macOS / WSL
.\start.ps1         # Windows (PowerShell)
```

Ce script :
1. Vérifie Python, Node.js et Docker
2. Demande la clé Groq si `GROQ_API_KEY` n'est pas définie
3. Crée un environnement virtuel Python dans `venv/`
4. Installe les dépendances Python (`requirements.txt` de chaque service)
5. Installe les dépendances npm du frontend
6. Démarre les 4 services en arrière-plan avec logs dans `logs/`

Accès : **http://localhost:5173**

---

### Étape 3 — Arrêter les services

```bash
./stop.sh           # Linux / macOS / WSL
.\stop.ps1          # Windows (PowerShell)
```

---

### Clé API Groq

```bash
# Option A — variable d'environnement (recommandé)
export GROQ_API_KEY="gsk_xxxxxxxxxxxx"
./start.sh

# Option B — saisie interactive
./start.sh
# → Le script vous demandera la clé si GROQ_API_KEY n'est pas définie
```

---

## Endpoints API

### `sp500_back` · port 8000

#### Entreprises

```
GET  /api/company/list                       → Liste toutes les entreprises
GET  /api/company/info?code=AAPL             → Détails d'une entreprise
GET  /api/company/search?query=Microsoft     → Recherche par nom ou ticker
GET  /api/company/count                      → Nombre total d'entreprises
```

#### Prix OHLCV

```
GET  /api/price/list?code=AAPL&start_date=2025-01-01&end_date=2025-06-01
GET  /api/price/latest?code=AAPL             → Dernier prix enregistré
GET  /api/price/statistics?code=AAPL         → Min, max, moyenne, volume total
GET  /api/price/count?code=AAPL              → Nombre de points disponibles
```

#### Prédictions ML (orchestrées)

```
GET  /api/prediction/?code=AAPL&steps=20&granularity=day
     → { ticker, predictions: [...], last_known_close, last_known_date, prediction_mode }

GET  /api/prediction/health                  → Vérifie que sp500_ml est accessible
```

#### Backtest

```
GET  /api/backtest/?code=MSFT&steps=10&granularity=day
     → Simule une prédiction faite N steps avant la fin des données
     → Compare les valeurs prédites aux vraies valeurs
     → Retourne MAE, RMSE, MAPE + détail step par step

Paramètres :
  code        Ticker S&P 500 (obligatoire)
  steps       1–500 — nombre de steps à tester (défaut : 10)
  granularity day | 15min | 30min (défaut : day)
```

Réponse backtest :
```json
{
  "ticker": "MSFT",
  "granularity": "day",
  "prediction_mode": "fallback",
  "context_length": 64,
  "test_steps": 10,
  "context_end_date": "2026-03-10",
  "context_end_close": 388.12,
  "metrics": { "mae": 1.24, "rmse": 1.87, "mape": 0.33 },
  "steps": [
    { "step": 1, "date": "2026-03-11", "predicted": 389.4, "actual": 387.8,
      "error": 1.6, "abs_error": 1.6, "pct_error": 0.41 },
    ...
  ]
}
```

#### Base de données (SQL brut)

```
POST /db/query   { "query": "SELECT code, name FROM company_data LIMIT 10" }
```

---

### `sp500_ml` · port 8002

```
POST /predict/
     Corps : { "ticker": "AAPL", "close_values": [<64 floats>], "steps": 30 }
     → { "predictions": [<N floats>], "mode": "dedicated_scaler|fallback",
         "prediction_length": 30 }

GET  /health     → { "status": "ok", "model_loaded": true }
```

---

### `sp500_ia` · port 8001

```
POST /ask/companyinfo/data
     Corps : { "ticker": "AAPL", "ohlcv_data": [...], "question": "..." }
     → Analyse IA des données OHLCV d'une action (mode Viewer)

POST /ask/ia/sqlproxy
     Corps : { "question": "Quel est le ticker avec le plus de volume ?" }
     → Génère une requête SQL, l'exécute et renvoie l'interprétation

POST /ask/ia/analyst
     Corps : { "companies": ["AAPL","MSFT"], "ohlcv_summaries": {...}, "question": "..." }
     → Analyse comparative multi-entreprises (mode AI Analyst)
```

---

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `GROQ_API_KEY` | _(obligatoire)_ | Clé API Groq pour le service LLM |
| `DB_USER` | `sp500_main` | Utilisateur MySQL |
| `DB_PASSWORD` | `sp500_main` | Mot de passe MySQL |
| `DB_HOST` | `localhost` | Hôte MySQL |
| `DB_PORT` | `3306` | Port MySQL |
| `DB_NAME` | `sp500` | Nom de la base de données |
| `ML_API_URL` | `http://localhost:8002` | URL interne du service ML |
| `CONTEXT_LENGTH` | `64` | Points historiques envoyés au modèle PatchTST |

---

## Structure du projet

```
s-p500-analysis/
├── setup.sh / setup.ps1            # Création Docker + chargement SQL (première fois)
├── start.sh / start.ps1            # Lancement de tous les services
├── stop.sh  / stop.ps1             # Arrêt de tous les services
├── Dockerfile                      # Image MySQL 8.0 préconfigurée
├── generate_pdf.py                 # Génère README.pdf via weasyprint + markdown2
│
├── sp500_back/                     # API principale (FastAPI · port 8000)
│   ├── main.py
│   ├── requirements.txt
│   ├── route/
│   │   ├── companies.py            # /api/company/
│   │   ├── prices.py               # /api/price/
│   │   ├── prediction.py           # /api/prediction/ — orchestre l'appel ML
│   │   ├── backtest.py             # /api/backtest/ — simulation rétrospective
│   │   └── globale.py              # /db/query — SQL brut
│   └── database/
│       ├── models.py               # Modèles SQLAlchemy
│       ├── session.py              # Connexion MySQL
│       ├── company_dao.py          # CRUD entreprises
│       └── price_dao.py            # Accès aux prix OHLCV
│
├── sp500_ml/                       # Service ML (FastAPI · port 8002)
│   ├── main.py
│   ├── requirements.txt
│   ├── route/predict.py            # POST /predict/
│   └── ml/
│       ├── predictor.py            # Singleton PatchTST, normalisation, inférence
│       └── patchtst_saved/         # Modèle pré-entraîné + scalers dédiés par ticker
│
├── sp500_ia/                       # Service LLM (FastAPI · port 8001)
│   ├── main.py                     # Endpoints Groq (companyinfo, sqlproxy, analyst)
│   └── requirements.txt
│
├── sp500_front/                    # Frontend (Vue 3 + TypeScript + Tailwind · port 5173)
│   └── src/
│       ├── views/
│       │   ├── HomeView.vue        # Page d'accueil — cartes de navigation
│       │   ├── Viewer.vue          # Bougies japonaises + chat IA
│       │   ├── AIAnalyst.vue       # Chatbot multi-entreprises + SQL naturel
│       │   ├── PredictionView.vue  # ML Prediction avec granularité + export CSV
│       │   └── SectorExplorer.vue  # ML + IA par secteur GICS + export CSV/TXT
│       ├── fetchers/               # Clients HTTP typés vers les APIs
│       ├── config/
│       │   ├── public-env.ts       # Ports et URLs des services
│       │   └── sectors.ts          # 11 secteurs GICS avec leurs tickers S&P 500
│       └── components/             # Nav, Footer, HomeCard, TextBox
│
├── tests/
│   ├── run_backtests.py            # Script : 13 tickers × 7 horizons × 3 granularités
│   ├── backtest_summary.csv        # Résumé des métriques (MAE, RMSE, MAPE)
│   ├── backtest_day_*.csv          # Détail par step — granularité jour
│   ├── backtest_15min_*.csv        # Détail par step — granularité 15 min
│   ├── backtest_30min_*.csv        # Détail par step — granularité 30 min
│   └── COVERAGE.md                 # Rapport complet de couverture des tests
│
└── SQL_Output/                     # Fichiers SQL à charger dans MySQL
    └── SQL_Output_compiled/
        └── SQL_Output/             # ~500 fichiers .sql (un par ticker)
```

---

## Schéma de la base de données

```sql
-- Répertoire des entreprises
CREATE TABLE company_data (
    companyIdx  INT          PRIMARY KEY,
    code        CHAR(10)     NOT NULL,   -- ticker boursier (ex: AAPL)
    name        VARCHAR(100) NOT NULL    -- nom complet
);

-- Données de prix — une table par ticker (ex: AAPL, MSFT, NVDA...)
CREATE TABLE AAPL (
    companyId   INT,
    date        DATETIME,               -- horodatage intraday (15 min)
    open        DECIMAL(10,4),
    low         DECIMAL(10,4),
    high        DECIMAL(10,4),
    close       DECIMAL(10,4),
    volume      BIGINT
);
```

> Les tables de prix contiennent des données **intraday à 15 minutes** sur environ 2 mois.
> Pour le mode `day`, les données sont agrégées par journée (dernier close retenu).

---

## Lecture des données OHLCV

| Colonne | Signification |
|---------|---------------|
| **Open** | Prix d'ouverture de la période |
| **High** | Prix le plus haut atteint |
| **Low** | Prix le plus bas atteint |
| **Close** | Prix de clôture de la période |
| **Volume** | Nombre d'actions échangées |

### Interprétation des bougies japonaises

| Signal | Interprétation |
|--------|----------------|
| Close > Open | Bougie haussière (verte) |
| Close < Open | Bougie baissière (rouge) |
| High ≈ Close | Les acheteurs ont dominé jusqu'à la clôture |
| Low ≈ Close | Les vendeurs ont dominé la séance |
| Volume élevé | Fort intérêt — événement ou volatilité importante |
| Volume faible | Marché calme, peu d'activité ou heure creuse |

---

## Modèle ML — PatchTST

PatchTST (**Patch Time Series Transformer**) est un modèle transformer sans cellule récurrente (LSTM-free), spécialisé dans la prédiction de séries temporelles univariées.

### Fonctionnement

1. **Entrée** : 64 derniers prix de clôture d'un ticker
2. **Patching** : la séquence est découpée en patches chevauchants, traités comme des tokens
3. **Transformer** : les tokens sont encodés et les dépendances temporelles sont apprises via l'auto-attention
4. **Sortie** : N prédictions consécutives (configurable via `steps`)

### Modes d'inférence

| Mode | Condition | Description |
|------|-----------|-------------|
| `dedicated_scaler` | Ticker connu du modèle | Scaler pré-entraîné sur les données du ticker — normalisation optimale |
| `fallback` | Ticker sans scaler dédié | Normalisation calculée à la volée sur les 64 valeurs reçues |

### Prédiction en cascade

Si `steps` dépasse la longueur de prédiction native du modèle, les sorties du premier batch sont réinjectées comme nouveau contexte pour générer les étapes suivantes. La précision peut décliner légèrement sur les horizons lointains.

---

## Backtesting

Le backtest simule une prédiction faite dans le passé et compare le résultat aux vraies valeurs.

```
Données réelles : [───── contexte (64 pts) ─────][── test (N pts) ──]
                                                  ↑
                                   prédiction lancée depuis ici
```

### Métriques retournées

| Métrique | Formule | Interprétation |
|----------|---------|----------------|
| **MAE** | moyenne de \|prédit − réel\| | Erreur moyenne en dollars |
| **RMSE** | √(moyenne de (prédit−réel)²) | Penalise les grandes erreurs |
| **MAPE** | moyenne de \|prédit−réel\| / réel × 100 | Erreur en % — comparable entre tickers |

### Lancer les tests de couverture

```bash
# Depuis la racine du projet (avec start.sh actif)
python tests/run_backtests.py
```

Génère `tests/backtest_summary.csv` et les fichiers détaillés par granularité.

Voir le rapport complet : [tests/COVERAGE.md](tests/COVERAGE.md)

---

## Résultats des backtests (synthèse)

273 tests effectués : **13 tickers × 7 horizons (10→70 steps) × 3 granularités**

| Granularité | MAPE moyen | Meilleur ticker | Pire ticker |
|-------------|-----------|-----------------|-------------|
| `day` | ~0.3 – 0.8% | V, MA, JPM | TSLA, NVDA |
| `15min` | ~0.05 – 0.2% | PEP, JNJ | TSLA |
| `30min` | ~0.05 – 0.2% | PEP, JNJ | TSLA |

> Les granularités intraday (15min, 30min) obtiennent de meilleures MAPE car les variations
> entre deux pas de 15 minutes sont naturellement plus faibles qu'entre deux jours.
