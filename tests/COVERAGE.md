# ML Backtest — Test Coverage

**Date d'exécution :** 2026-03-29
**Endpoint testé :** `GET /api/backtest/?code={ticker}&steps={n}&granularity={gran}`
**Modèle ML :** PatchTST — mode `fallback`
**Contexte :** 64 points (day : adapté aux données disponibles)
**Granularités :** `day` (1 step = 1 jour), `15min`, `30min`
**Horizons :** 10, 20, 30, 40, 50, 60, 70 steps

---

## Glossaire — Termes et métriques

### Principe du backtest
Le backtest simule une prédiction "dans le passé" : on masque les **N derniers points connus**
de la base de données, on lance le modèle ML sur les 64 points qui précèdent, puis on compare
chaque valeur prédite à la vraie valeur enregistrée. Cela permet de mesurer la précision réelle
du modèle sur des données qu'il n'a jamais vues.

```
Données réelles : [... contexte (64 pts) ...][... test (N pts) ...]
                                             ↑
                              le modèle prédit à partir d'ici
```

### Granularités

| Terme | Signification | Exemple pour 10 steps |
|-------|--------------|----------------------|
| `day` | 1 step = 1 jour de bourse | 10 jours calendaires (~2 semaines) |
| `15min` | 1 step = 15 minutes | 10 × 15 min = 2h30 de marché |
| `30min` | 1 step = 30 minutes | 10 × 30 min = 5h de marché |

> Les données en base sont en granularité **intraday** (minutes). Pour le mode `day`,
> les rows sont agrégés par journée (dernier close de chaque jour).

### Métriques de précision

| Métrique | Formule | Interprétation |
|----------|---------|----------------|
| **MAE** (Mean Absolute Error) | moyenne de \|prédit − réel\| | Erreur moyenne en dollars. Ex: MAE=0.5$ → en moyenne 0.5$ d'écart. |
| **RMSE** (Root Mean Square Error) | √(moyenne de (prédit−réel)²) | Pénalise davantage les grandes erreurs. Toujours ≥ MAE. |
| **MAPE** (Mean Absolute Percentage Error) | moyenne de \|prédit−réel\| / réel × 100 | Erreur en %. Indépendant du cours absolu — permet de comparer TSLA (~430$) et PEP (~152$). |

### Barème qualité (basé sur MAPE)

| MAPE | Label | Interprétation |
|------|-------|----------------|
| < 1% | **Excellent** | Prédiction très précise, utilisable en production |
| 1–3% | **Bon** | Légère dérive, bon pour analyse de tendance |
| 3–5% | **Acceptable** | Indicatif seulement, erreur notable sur prix absolu |
| 5–10% | **Imprécis** | Tendance globale correcte mais valeurs peu fiables |
| > 10% | **Mauvais** | Prédiction peu exploitable |

### Symboles utilisés dans les tableaux

| Symbole | Signification |
|---------|--------------|
| ✅ | MAPE < 3% — Bon à Excellent |
| ⚠️ | MAPE 3–10% — Acceptable à Imprécis |
| ❌ | MAPE > 10% — Mauvais |

### Modes du modèle PatchTST

| Mode | Description |
|------|-------------|
| `dedicated_scaler` | Le ticker possède un scaler pré-entraîné — normalisation optimisée, plus précis |
| `fallback` | Pas de scaler dédié — normalisation calculée à la volée sur le contexte reçu |

> Tous les tests de ce document tournent en mode **`fallback`** — aucun scaler dédié n'est disponible pour ces tickers.

---

## Tickers testés (13)

| Ticker | Secteur | Cours approx. |
|--------|---------|--------------|
| MSFT | Information Technology | ~525 $ |
| NVDA | Information Technology | ~186 $ |
| TSLA | Consumer Discretionary | ~430 $ |
| GOOGL | Communication Services | ~260 $ |
| META | Communication Services | ~740 $ |
| JPM | Financials | ~300 $ |
| JNJ | Health Care | ~190 $ |
| XOM | Energy | ~115 $ |
| HD | Consumer Discretionary | ~387 $ |
| V | Financials | ~349 $ |
| MA | Financials | ~575 $ |
| PEP | Consumer Staples | ~152 $ |
| COST | Consumer Staples | ~932 $ |

> AAPL et AMZN absents de la base (HTTP 404).

---

## Synthèse globale

| Granularité | Steps | Tickers | MAPE moyen | MAPE min | MAPE max | Qualité |
|-------------|-------|---------|-----------|---------|---------|---------|
| 15min | 10 | 13 | 0.050% | 0.016% (GOOGL) | 0.167% (MA) | **Excellent** |
| 15min | 20 | 13 | 0.090% | 0.022% (JNJ) | 0.260% (PEP) | **Excellent** |
| 15min | 30 | 13 | 0.102% | 0.017% (META) | 0.353% (MA) | **Excellent** |
| 15min | 40 | 13 | 0.133% | 0.030% (META) | 0.372% (MA) | **Excellent** |
| 15min | 50 | 13 | 0.209% | 0.049% (META) | 0.480% (NVDA) | **Excellent** |
| 15min | 60 | 13 | 0.251% | 0.074% (MSFT) | 0.523% (NVDA) | **Excellent** |
| 15min | 70 | 13 | 0.294% | 0.089% (V) | 0.649% (NVDA) | **Excellent** |
| 30min | 10 | 13 | 0.183% | 0.073% (PEP) | 0.467% (TSLA) | **Excellent** |
| 30min | 20 | 13 | 0.322% | 0.108% (MA) | 1.233% (TSLA) | **Excellent** |
| 30min | 30 | 13 | 0.438% | 0.137% (PEP) | 1.650% (TSLA) | **Excellent** |
| 30min | 40 | 13 | 0.802% | 0.172% (MSFT) | 2.112% (TSLA) | Excellent/Bon |
| 30min | 50 | 13 | 0.726% | 0.263% (META) | 1.716% (TSLA) | **Excellent** |
| 30min | 60 | 13 | 0.571% | 0.207% (MSFT) | 1.520% (TSLA) | Excellent/Bon |
| 30min | 70 | 13 | 0.572% | 0.232% (MA) | 1.278% (TSLA) | Excellent/Bon |
| day | 10 | 13 | 2.358% | 0.726% (MA) | 5.600% (XOM) | Bon/Acceptable |
| day | 20 | 13 | 3.688% | 1.334% (V) | 9.729% (TSLA) | Acceptable |
| day | 30 | 13 | 4.226% | 1.408% (COST) | 12.291% (TSLA) | Acceptable/Imprécis |
| day | 40 | 13 | 4.615% | 1.980% (COST) | 10.807% (TSLA) | Acceptable/Imprécis |
| day | 50 | 13 | 4.955% | 2.396% (PEP) | 9.773% (TSLA) | Acceptable/Imprécis |
| day | 60 | 13 | 5.559% | 2.187% (PEP) | 10.002% (XOM) | Imprécis |
| day | 70 | 13 | 6.151% | 2.044% (PEP) | 10.622% (XOM) | Imprécis |

---
~~~~
## Évolution du MAPE moyen par horizon

```
Steps    15min       30min       day
  10     0.050 %    0.183 %    2.358 %
  20     0.090 %    0.322 %    3.688 %
  30     0.102 %    0.438 %    4.226 %
  40     0.133 %    0.802 %    4.615 %
  50     0.209 %    0.726 %    4.955 %
  60     0.251 %    0.571 %    5.559 %
  70     0.294 %    0.572 %    6.151 %
```

---

## Résultats détaillés — Granularité `day`

| Ticker | 10j | 20j | 30j | 40j | 50j | 60j | 70j |
|--------|-----|-----|-----|-----|-----|-----|-----|
| MA | 0.73% ✅ | 2.34% ✅ | 2.42% ✅ | 2.32% ✅ | 2.65% ✅ | 3.23% ✅ | 3.66% ✅ |
| COST | 0.76% ✅ | 1.49% ✅ | 1.41% ✅ | 1.98% ✅ | 2.91% ✅ | 4.87% ⚠️ | 6.21% ⚠️ |
| JPM | 1.12% ✅ | 1.90% ✅ | 1.75% ✅ | 2.53% ✅ | 3.63% ⚠️ | 5.19% ⚠️ | 6.64% ⚠️ |
| JNJ | 1.04% ✅ | 2.09% ✅ | 2.84% ✅ | 3.10% ⚠️ | 2.73% ✅ | 2.40% ✅ | 2.36% ✅ |
| V | 1.63% ✅ | 1.33% ✅ | 2.33% ✅ | 3.67% ⚠️ | 4.81% ⚠️ | 5.73% ⚠️ | 6.50% ⚠️ |
| MSFT | 2.03% ✅ | 2.62% ✅ | 4.93% ⚠️ | 7.24% ⚠️ | 8.56% ⚠️ | 9.40% ⚠️ | 10.06% ❌ |
| HD | 2.59% ✅ | 4.85% ⚠️ | 4.89% ⚠️ | 3.93% ⚠️ | 4.22% ⚠️ | 5.60% ⚠️ | 6.49% ⚠️ |
| GOOGL | 2.62% ✅ | 3.87% ⚠️ | 3.70% ⚠️ | 3.23% ⚠️ | 2.89% ✅ | 2.92% ✅ | 3.07% ⚠️ |
| TSLA | 2.40% ✅ | 9.73% ⚠️ | 12.29% ❌ | 10.81% ❌ | 9.77% ⚠️ | 8.43% ⚠️ | 8.04% ⚠️ |
| NVDA | 2.70% ✅ | 4.43% ⚠️ | 4.60% ⚠️ | 5.69% ⚠️ | 5.49% ⚠️ | 6.10% ⚠️ | 6.93% ⚠️ |
| META | 3.46% ⚠️ | 3.27% ⚠️ | 3.40% ⚠️ | 4.85% ⚠️ | 5.11% ⚠️ | 6.22% ⚠️ | 7.34% ⚠️ |
| PEP | 3.98% ⚠️ | 4.42% ⚠️ | 3.46% ⚠️ | 2.77% ✅ | 2.40% ✅ | 2.19% ✅ | 2.04% ✅ |
| XOM | 5.60% ⚠️ | 5.59% ⚠️ | 6.93% ⚠️ | 7.88% ⚠️ | 9.25% ⚠️ | 10.00% ❌ | 10.62% ❌ |

> ✅ < 3% — ⚠️ 3–10% — ❌ > 10%

---

## Résultats détaillés — Granularité `15min`

| Ticker | 10 | 20 | 30 | 40 | 50 | 60 | 70 |
|--------|----|----|----|----|----|----|-----|
| GOOGL | 0.016% | 0.071% | 0.032% | 0.065% | 0.324% | 0.353% | 0.410% |
| META | 0.016% | 0.046% | 0.017% | 0.030% | 0.049% | 0.177% | 0.217% |
| TSLA | 0.019% | 0.120% | 0.090% | 0.167% | 0.223% | 0.329% | 0.419% |
| MSFT | 0.022% | 0.043% | 0.039% | 0.179% | 0.159% | 0.074% | 0.136% |
| COST | 0.017% | 0.032% | 0.027% | 0.058% | 0.061% | 0.183% | 0.394% |
| JNJ | 0.032% | 0.022% | 0.032% | 0.096% | 0.076% | 0.160% | 0.303% |
| JPM | 0.031% | 0.055% | 0.147% | 0.208% | 0.463% | 0.468% | 0.330% |
| XOM | 0.041% | 0.038% | 0.076% | 0.064% | 0.165% | 0.096% | 0.111% |
| V | 0.050% | 0.103% | 0.072% | 0.074% | 0.161% | 0.121% | 0.089% |
| HD | 0.058% | 0.176% | 0.221% | 0.195% | 0.186% | 0.332% | 0.329% |
| PEP | 0.104% | 0.260% | 0.089% | 0.118% | 0.083% | 0.177% | 0.194% |
| NVDA | 0.081% | 0.067% | 0.129% | 0.103% | 0.480% | 0.523% | 0.649% |
| MA | 0.167% | 0.133% | 0.353% | 0.372% | 0.292% | 0.264% | 0.242% |

---

## Résultats détaillés — Granularité `30min`

| Ticker | 10 | 20 | 30 | 40 | 50 | 60 | 70 |
|--------|----|----|----|----|----|----|-----|
| PEP | 0.073% | 0.146% | 0.137% | 0.210% | 0.266% | 0.262% | 0.259% |
| MA | 0.085% | 0.108% | 0.388% | 0.303% | 0.726% | 0.231% | 0.232% |
| XOM | 0.084% | 0.314% | 0.266% | 0.529% | 0.324% | 0.300% | 0.255% |
| MSFT | 0.149% | 0.259% | 0.198% | 0.172% | 0.460% | 0.207% | 0.353% |
| JPM | 0.148% | 0.125% | 0.727% | 1.690% | 1.564% | 1.282% | 1.131% |
| GOOGL | 0.127% | 0.245% | 0.250% | 1.620% | 1.225% | 0.943% | 1.236% |
| HD | 0.217% | 0.129% | 0.180% | 0.707% | 0.526% | 0.409% | 0.368% |
| COST | 0.119% | 0.296% | 0.600% | 0.949% | 0.484% | 0.414% | 0.386% |
| V | 0.104% | 0.303% | 0.290% | 0.210% | 0.288% | 0.233% | 0.243% |
| NVDA | 0.411% | 0.288% | 0.241% | 0.721% | 0.919% | 0.824% | 0.942% |
| JNJ | 0.192% | 0.281% | 0.452% | 0.839% | 0.680% | 0.564% | 0.514% |
| META | 0.202% | 0.462% | 0.309% | 0.359% | 0.263% | 0.232% | 0.233% |
| TSLA | 0.467% | 1.233% | 1.650% | 2.112% | 1.716% | 1.520% | 1.278% |

---

## Observations

### 15min — Excellent sur toute la plage
- **100% des résultats Excellent** (MAPE < 1%) sur 7 horizons × 13 tickers.
- MAPE moyen reste sous **0.30%** même à 70 steps.
- Meilleurs tickers : META, GOOGL, MSFT, XOM. Moins bon : NVDA (volatilité élevée).

### 30min — Très bon, TSLA difficile
- **TSLA** est le seul ticker à dépasser 1% de MAPE régulièrement (jusqu'à 2.1% à 40 steps).
- JPM et GOOGL se dégradent à partir de 40 steps (>1% MAPE) mais restent en zone acceptable.
- Le reste reste **Excellent** sur toute la plage.

### day — Précision attendue plus faible
- Le modèle PatchTST est entraîné principalement sur données intraday — les prédictions journalières sont moins précises.
- MAPE moyen entre **2.4% (10j) et 6.2% (70j)** — zone "Bon" à "Imprécis".
- **Meilleurs sur horizons courts** : MA, COST, JPM, JNJ restent en zone "Bon" (MAPE < 3%).
- **TSLA et XOM** sont les plus difficiles en journalier (jusqu'à 12.3% et 10.6%).
- **PEP et JNJ** résistent bien sur les longs horizons (MAPE ~2% à 70j).

### Recommandation d'usage
| Usage | Granularité recommandée | Horizon max fiable |
|-------|------------------------|-------------------|
| Trading intraday | 15min | 70 steps (~17h) |
| Analyse demi-journée | 30min | 30 steps (~15h) |
| Vision hebdomadaire | day | 10–20 jours |
| Vision mensuelle | day | à utiliser avec précaution |

---

## Barème qualité MAPE

| Seuil | Label |
|-------|-------|
| < 1% | Excellent |
| 1–3% | Bon |
| 3–5% | Acceptable |
| 5–10% | Imprécis |
| > 10% | Mauvais |

---

## Fichiers générés (22 fichiers)

| Fichier | Lignes de données |
|---------|-----------------|
| `backtest_day_10steps.csv` | 13 × 10 = 130 |
| `backtest_day_20steps.csv` | 13 × 20 = 260 |
| `backtest_day_30steps.csv` | 13 × 30 = 390 |
| `backtest_day_40steps.csv` | 13 × 40 = 520 |
| `backtest_day_50steps.csv` | 13 × 50 = 650 |
| `backtest_day_60steps.csv` | 13 × 60 = 780 |
| `backtest_day_70steps.csv` | 13 × 70 = 910 |
| `backtest_15min_10steps.csv` | 130 |
| `backtest_15min_20steps.csv` | 260 |
| `backtest_15min_30steps.csv` | 390 |
| `backtest_15min_40steps.csv` | 520 |
| `backtest_15min_50steps.csv` | 650 |
| `backtest_15min_60steps.csv` | 780 |
| `backtest_15min_70steps.csv` | 910 |
| `backtest_30min_10steps.csv` | 130 |
| `backtest_30min_20steps.csv` | 260 |
| `backtest_30min_30steps.csv` | 390 |
| `backtest_30min_40steps.csv` | 520 |
| `backtest_30min_50steps.csv` | 650 |
| `backtest_30min_60steps.csv` | 780 |
| `backtest_30min_70steps.csv` | 910 |
| `backtest_summary.csv` | 273 entrées (13 × 7 × 3) |
