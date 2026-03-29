# S&P 500 Analysis Platform

Plateforme complète d'analyse des actions du S&P 500 combinant visualisation de données historiques, prédictions par deep learning (PatchTST) et analyse financière en langage naturel via LLM (Groq / llama-3.3-70b).

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│               sp500_front  (Vue 3 · port 5173)           │
└────────┬─────────────────┬──────────────────┬────────────┘
         │                 │                  │
         ▼                 ▼                  ▼
┌─────────────────┐ ┌────────────┐  ┌──────────────────┐
│   sp500_back    │ │  sp500_ml  │  │    sp500_ia       │
│  API principale │ │  API ML    │  │  API LLM          │
│   port 8000     │ │  port 8002 │  │  port 8001        │
└────────┬────────┘ └─────┬──────┘  └────────┬──────────┘
         │                │                   │
         ▼                ▼                   ▼
┌─────────────────┐ ┌────────────┐  ┌──────────────────┐
│  MySQL · 3306   │ │  PatchTST  │  │  Groq API (LLM)  │
│  (Docker)       │ │  (modèle)  │  │  llama-3.3-70b   │
└─────────────────┘ └────────────┘  └──────────────────┘
```

---

## Services et ports

| Service | Port | Rôle |
|---------|------|------|
| `sp500_front` | 5173 | Interface web Vue 3 |
| `sp500_back` | 8000 | API REST principale (données OHLCV + orchestration ML) |
| `sp500_ia` | 8001 | Analyse financière LLM (Groq) |
| `sp500_ml` | 8002 | Prédictions de prix (PatchTST) |
| MySQL | 3306 | Base de données (Docker) |

---

## Vues disponibles

### Data Viewer
Graphique en bougies japonaises (lightweight-charts) pour chaque action du S&P 500. Inclut un chat IA intégré pour poser des questions sur les données OHLCV affichées.

### AI Analyst
Sélection multi-entreprises par checkboxes avec recherche. Deux modes :
- **Chat** — analyse comparative multi-entreprises, détection d'anomalies, tendances
- **SQL** — génération et exécution de requêtes SQL depuis une question en langage naturel

### ML Prediction
Prédictions de prix via PatchTST avec choix de la granularité (jours / heures / 15 min) et du nombre de pas. Affiche un graphique combinant historique réel et ligne de prédiction, ainsi qu'un tableau des valeurs estimées.

### Sector Explorer
Vue d'analyse sectorielle GICS. Sélection d'entreprises par secteur, lancement des prédictions ML en parallèle, puis analyse IA croisée interprétant l'ensemble des prédictions du secteur. Affiche des sparklines par ticker et un tableau récapitulatif.

---

## Installation et démarrage

### Prérequis
- Python 3.8+
- Node.js 18+ et npm
- Docker

### 1. Première installation — base de données MySQL

```bash
./setup.sh
```

Ce script :
- Construit l'image Docker MySQL 8.0
- Crée le conteneur `my_sp500_db`
- Attend que MySQL soit prêt
- Charge tous les fichiers SQL depuis `SQL_Output/SQL_Output_compiled/SQL_Output/`

> A effectuer une seule fois. Si le conteneur existe déjà, le script propose de le recréer.

### 2. Lancement de la plateforme

**Linux / macOS / WSL :**
```bash
./start.sh
```

**Windows (PowerShell) :**
```powershell
.\start.ps1
```

Ces scripts :
- Vérifient Python, Node.js et Docker
- Demandent la clé Groq si elle n'est pas définie en variable d'environnement
- Créent et activent un venv Python
- Installent toutes les dépendances Python et npm
- Démarrent les 4 services en arrière-plan avec logs dans `logs/`

### 3. Arrêt des services

```bash
./stop.sh        # Linux/macOS/WSL
.\stop.ps1       # Windows
```

---

## Clé API Groq

1. Créer un compte et générer une clé sur : https://console.groq.com/keys
2. Exporter la variable avant le lancement :

```bash
export GROQ_API_KEY="votre_clé_ici"
./start.sh
```

Ou laisser `start.sh` / `start.ps1` vous la demander interactivement au démarrage.

---

## Endpoints API

### sp500_back (port 8000)

```
GET  /api/company/list
GET  /api/company/info?code=AAPL
GET  /api/company/search?query=Air
GET  /api/company/count

GET  /api/price/list?code=AAPL&start_date=2025-01-01&end_date=2025-06-01
GET  /api/price/latest?code=AAPL
GET  /api/price/statistics?code=AAPL
GET  /api/price/count?code=AAPL

GET  /api/prediction/?code=AAPL&steps=20&granularity=day
GET  /api/prediction/health

POST /db/query   { "query": "SELECT ..." }
```

### sp500_ml (port 8002)

```
POST /predict/
     { "ticker": "AAPL", "close_values": [...64 valeurs...], "steps": 30 }
     → { "predictions": [...], "mode": "dedicated_scaler|fallback", "prediction_length": 30 }

GET  /health
```

### sp500_ia (port 8001)

```
POST /ask/companyinfo/data   → Analyse les données OHLCV d'une action
POST /ask/ia/sqlproxy        → Génère et exécute une requête SQL depuis une question naturelle
POST /ask/ia/analyst         → Analyse comparative multi-entreprises
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
| `DB_NAME` | `sp500` | Nom de la base |
| `ML_API_URL` | `http://localhost:8002` | URL du service ML |
| `CONTEXT_LENGTH` | `64` | Nombre de points historiques envoyés au modèle PatchTST |

---

## Structure du projet

```
s-p500-analysis/
├── setup.sh / setup.ps1         # Installation Docker + chargement SQL (première fois)
├── start.sh / start.ps1         # Lancement de tous les services
├── stop.sh  / stop.ps1          # Arrêt de tous les services
├── Dockerfile                   # Image MySQL 8.0 préconfigurée
│
├── sp500_back/                  # API principale (FastAPI · port 8000)
│   ├── main.py
│   ├── route/
│   │   ├── companies.py         # /api/company/
│   │   ├── prices.py            # /api/price/
│   │   ├── prediction.py        # /api/prediction/ — orchestre l'appel ML
│   │   └── globale.py           # /db/query
│   └── database/
│       ├── models.py            # Modèles SQLAlchemy
│       ├── session.py           # Connexion MySQL
│       ├── company_dao.py       # CRUD entreprises
│       └── price_dao.py         # Accès aux prix
│
├── sp500_ml/                    # Service ML (FastAPI · port 8002)
│   ├── main.py
│   ├── route/predict.py         # POST /predict/
│   └── ml/
│       ├── predictor.py         # Singleton PatchTST, normalisation, inférence
│       └── patchtst_saved/      # Modèle pré-entraîné + scalers par ticker
│
├── sp500_ia/                    # Service LLM (FastAPI · port 8001)
│   └── main.py                  # Endpoints Groq (companyinfo, sqlproxy, analyst)
│
├── sp500_front/                 # Frontend (Vue 3 + TypeScript + Tailwind · port 5173)
│   └── src/
│       ├── views/
│       │   ├── HomeView.vue
│       │   ├── Viewer.vue       # Bougies japonaises + chat IA
│       │   ├── AIAnalyst.vue    # Chatbot multi-entreprises + SQL naturel
│       │   ├── PredictionView.vue  # ML Prediction avec granularité
│       │   └── SectorExplorer.vue  # ML + IA par secteur GICS
│       ├── fetchers/            # Clients HTTP vers les APIs
│       ├── config/
│       │   ├── public-env.ts    # Ports et URLs
│       │   └── sectors.ts       # 11 secteurs GICS avec tickers S&P 500
│       └── components/          # Nav, Footer, HomeCard, TextBox
│
└── SQL_Output/                  # Fichiers SQL à charger dans MySQL
    └── SQL_Output_compiled/
        └── SQL_Output/
```

---

## Schéma de la base de données

```sql
-- Table des entreprises
company_data (
    companyIdx  INT PRIMARY KEY,
    code        CHAR(10),
    name        VARCHAR(100)
)

-- Une table de prix par ticker (ex: AAPL, MSFT, NVDA...)
AAPL (
    companyId   INT,
    date        DATETIME,
    open        DECIMAL,
    low         DECIMAL,
    high        DECIMAL,
    close       DECIMAL,
    volume      BIGINT
)
```

---

## Lecture des données OHLCV

| Colonne | Signification |
|---------|---------------|
| **Open** | Prix d'ouverture |
| **High** | Prix le plus haut de la journée |
| **Low** | Prix le plus bas de la journée |
| **Close** | Prix de clôture |
| **Volume** | Nombre d'actions échangées |

| Signal | Interprétation |
|--------|----------------|
| Close > Open | Journée haussière |
| Close < Open | Journée baissière |
| High ≈ Close | Les acheteurs ont dominé jusqu'à la clôture |
| Low ≈ Close | Les vendeurs ont dominé la séance |
| Volume élevé | Fort intérêt — événement ou volatilité |
| Volume faible | Marché calme, peu d'activité |

---

## Modèle ML — PatchTST

- **Entrée** : 64 derniers prix de clôture d'un ticker
- **Sortie** : N prédictions (configurable via le paramètre `steps`)
- **Mode `dedicated_scaler`** : ticker connu, scaler pré-entraîné — plus précis
- **Mode `fallback`** : normalisation à la volée pour les tickers sans scaler dédié
- **Prédictions en cascade** : si `steps` dépasse la longueur de prédiction native du modèle, les sorties sont réinjectées comme nouveau contexte
