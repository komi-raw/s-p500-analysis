# S&P 500 Analysis Platform

Plateforme complète d'analyse des actions du S&P 500 combinant visualisation de données historiques, prédictions par intelligence artificielle (PatchTST) et analyse financière via LLM (Grok-3).

---

## But du projet

Permettre l'analyse approfondie des actions du S&P 500 :

- Consultation des **données historiques** OHLCV pour chaque action
- **Prédictions de prix** futures via un modèle deep learning (PatchTST)
- **Analyse financière** en langage naturel via Grok-3 (xAI)
- **Interface web** interactive avec graphiques financiers en bougies japonaises

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│               sp500_front  (Vue 3 · port 5173)       │
└────────┬─────────────────┬────────────────┬──────────┘
         │                 │                │
         ▼                 ▼                ▼
┌─────────────────┐ ┌────────────┐ ┌──────────────────┐
│   sp500_back    │ │  sp500_ml  │ │    sp500_ia       │
│  API principale │ │  API ML    │ │  API LLM          │
│   port 8000     │ │  port 8002 │ │  port 8001        │
└────────┬────────┘ └─────┬──────┘ └────────┬──────────┘
         │                │                  │
         ▼                ▼                  ▼
┌─────────────────┐ ┌────────────┐  ┌──────────────────┐
│   MySQL (ORM)   │ │  PatchTST  │  │   Grok-3 (xAI)   │
│   port 3306     │ │  (modèle)  │  │      API         │
└─────────────────┘ └────────────┘  └──────────────────┘
```

---

## Services et ports

| Service | Port | Rôle |
|---------|------|------|
| `sp500_front` | 5173 | Interface web Vue 3 |
| `sp500_back` | 8000 | API REST principale (données + orchestration) |
| `sp500_ia` | 8001 | Chatbot financier LLM (Grok-3) |
| `sp500_ml` | 8002 | Prédictions de prix (PatchTST) |
| MySQL | 3306 | Base de données |

---

## Structure des dossiers

### `database/` — Couche d'accès aux données

Modèles SQLAlchemy et DAO pour interagir avec MySQL.

| Fichier | Rôle |
|---------|------|
| `models.py` | Modèle `CompanyData` + factory dynamique de tables de prix par ticker |
| `session.py` | Connexion MySQL via SQLAlchemy, configuration par variables d'environnement |
| `company_dao.py` | CRUD entreprises : liste, recherche, pagination |
| `price_dao.py` | Accès aux prix : historique, statistiques, plages de dates |

**Schéma :**
```sql
company_data  (companyIdx PK, code CHAR(10), name VARCHAR(100))
AAPL          (companyId, date, open, low, high, close, volume)  -- une table par ticker
```

---

### `sp500_back/` — API principale (FastAPI · port 8000)

Point d'entrée REST central. Expose les données et orchestre les appels ML.

| Fichier | Rôle |
|---------|------|
| `main.py` | App FastAPI, CORS, enregistrement des routers |
| `route/companies.py` | `/api/company/` — liste, info, recherche, comptage |
| `route/prices.py` | `/api/price/` — historique, dernier prix, statistiques |
| `route/prediction.py` | `/api/prediction/` — récupère les prix, agrège par jour, appelle sp500_ml |
| `route/globale.py` | `/db/query` — exécution SQL brute (debug) |

**Endpoints :**
```
GET /api/company/list
GET /api/company/info?code=AAPL
GET /api/company/search?query=Air
GET /api/company/count

GET /api/price/list?code=AAPL&start_date=2025-01-01&end_date=2025-06-01
GET /api/price/latest?code=AAPL
GET /api/price/statistics?code=AAPL
GET /api/price/count?code=AAPL

GET /api/prediction/?code=AAPL&steps=20
GET /api/prediction/health

POST /db/query   body: { "query": "SELECT ..." }
```

---

### `sp500_ml/` — Service ML (FastAPI · port 8002)

Prédictions de prix via le modèle **PatchTST** (HuggingFace Transformers).

| Fichier | Rôle |
|---------|------|
| `main.py` | App FastAPI, chargement du modèle au démarrage |
| `route/predict.py` | `POST /predict/` — inférence avec support cascade multi-steps |
| `ml/predictor.py` | Singleton du modèle, normalisation, inférence |
| `ml/patchtst_saved/` | Modèle pré-entraîné + scalers par ticker |

**Fonctionnement :**
- Entrée : 64 derniers prix de clôture d'un ticker
- Sortie : N prédictions (configurable via `steps`)
- Si `steps > prediction_length` du modèle : **prédictions en cascade** (réinjection des sorties comme nouveau contexte)
- Mode `dedicated_scaler` (ticker connu, plus précis) ou `fallback` (normalisation à la volée)

```
POST /predict/
{ "ticker": "APD", "close_values": [...64 valeurs...], "steps": 30 }
→ { "predictions": [...], "mode": "fallback", "prediction_length": 30 }

GET /health
```

---

### `sp500_ia/` — Service LLM (FastAPI · port 8001)

Analyse financière en langage naturel via l'API **Grok-3-Mini** (xAI).

| Fichier | Rôle |
|---------|------|
| `main.py` | App FastAPI + tous les endpoints LLM |

**Endpoints :**
```
POST /ask/companyinfo/data   → Analyse les données OHLCV d'une action
POST /ask/ia/sqlproxy        → Génère et exécute une requête SQL depuis une question naturelle
POST /ask/ia/analyst         → Analyse comparative multi-entreprises avec détection d'anomalies
```

**Configuration clé API :**
1. Obtenir une clé sur https://console.x.ai/
2. La renseigner dans `sp500_ia/main.py`

---

### `sp500_front/` — Interface web (Vue 3 · port 5173)

```
src/
├── views/
│   ├── HomeView.vue        → Accueil avec cartes de navigation
│   ├── Viewer.vue          → Graphique en bougies + infos entreprise + chat IA
│   ├── AIAnalyst.vue       → Chatbot financier (analyst / SQL naturel)
│   └── PredictionView.vue  → Prédictions ML avec graphique historique + ligne prédite
├── fetchers/
│   ├── GenericFetcher.ts   → Client HTTP Axios de base
│   ├── Company.ftc.ts      → Appels /api/company/
│   ├── Company2Stat.ftc.ts → Appels /api/price/
│   └── Prediction.ftc.ts   → Appels /api/prediction/
├── config/
│   ├── public-env.ts       → URLs (BACK_PORT=8000, BACK_IA_PORT=8001, BACK_ML_PORT=8002)
│   └── public-dat.ts       → Constantes
├── components/
│   ├── Nav.vue / Footer.vue / HomeCard.vue / TextBox.vue
└── objects/
    └── ChartCM.ts          → Wrapper lightweight-charts (bougies japonaises)
```

---

### `back/` — Backend Express.js (legacy)

Ancien serveur Node.js remplacé par `sp500_back`. Conservé à titre de référence.

---

### Fichiers à la racine

| Fichier | Rôle |
|---------|------|
| `Dockerfile` | Image MySQL 8.0 préconfigurée |
| `dockerBuild.sh` | Build de l'image Docker |
| `dockerRun.sh` | Lance le conteneur MySQL |
| `dockerAddData.sh` | Charge les fichiers SQL dans la base |
| `convertCsvToSql.py` | Convertit les CSV de prix en fichiers SQL |
| `export_data_info.py` | Utilitaire d'export |
| `extract_names_company.py` | Extraction des noms d'entreprises |

---

## Lecture des données OHLCV

| Colonne | Signification |
|---------|---------------|
| **Open** | Prix d'ouverture |
| **High** | Prix le plus haut |
| **Low** | Prix le plus bas |
| **Close** | Prix de clôture |
| **Volume** | Nombre d'actions échangées |

| Tendance | Signification |
|----------|---------------|
| Close > Open | Journée haussière |
| Close < Open | Journée baissière |
| Volume élevé | Forte activité, événement majeur |
| Volume faible | Marché calme |

---

## Lancer le projet

### 1. Base de données MySQL
```bash
./dockerBuild.sh
./dockerRun.sh
./dockerAddData.sh
```

### 2. API principale
```bash
cd sp500_back
uvicorn main:app --port 8000 --reload
```

### 3. Service LLM
```bash
cd sp500_ia
uvicorn main:app --port 8001 --reload
```

### 4. Service ML
```bash
cd sp500_ml
uvicorn main:app --port 8002 --reload
```

### 5. Frontend
```bash
cd sp500_front
npm install
npm run dev
```

---

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DB_USER` | `sp500_main` | Utilisateur MySQL |
| `DB_PASSWORD` | `sp500_main` | Mot de passe MySQL |
| `DB_HOST` | `localhost` | Hôte MySQL |
| `DB_PORT` | `3306` | Port MySQL |
| `DB_NAME` | `sp500` | Nom de la base |
| `ML_API_URL` | `http://localhost:8002` | URL du service ML |
| `CONTEXT_LENGTH` | `64` | Nombre de points historiques envoyés au modèle |
