"""
tests/run_backtests.py
----------------------
Lance des backtests sur 13 tickers × 7 horizons × 3 granularités :
  - Horizons : 10, 20, 30, 40, 50, 60, 70 steps
  - Granularités : day (1 step = 1 jour), 15min, 30min

Résultats sauvegardés dans :
  tests/backtest_day_<N>steps.csv
  tests/backtest_15min_<N>steps.csv
  tests/backtest_30min_<N>steps.csv
  tests/backtest_summary.csv
"""

import csv
import json
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8000"
OUT_DIR  = Path(__file__).parent

TICKERS = [
    "MSFT", "NVDA", "TSLA", "GOOGL", "META",
    "JPM",  "JNJ",  "XOM",  "HD",    "V",
    "MA",   "PEP",  "COST",
]

HORIZONS      = list(range(10, 71, 10))          # 10 20 30 40 50 60 70
GRANULARITIES = ["day", "15min", "30min"]


def fetch(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read())


def run_one(ticker: str, steps: int, granularity: str) -> dict | None:
    url = f"{BASE_URL}/api/backtest/?code={ticker}&steps={steps}&granularity={granularity}"
    try:
        return fetch(url)
    except Exception as e:
        print(f"  [ERREUR] {ticker} {granularity} steps={steps} → {e}")
        return None


def write_detail(results: list[dict], filename: str):
    path = OUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "ticker", "granularity", "mode", "context_end_date", "context_end_close",
            "step", "date", "predicted", "actual", "error", "abs_error", "pct_error"
        ])
        for r in results:
            for s in r["steps"]:
                writer.writerow([
                    r["ticker"], r["granularity"], r["prediction_mode"],
                    r["context_end_date"], r["context_end_close"],
                    s["step"], s["date"],
                    s["predicted"], s["actual"],
                    s["error"], s["abs_error"], s["pct_error"],
                ])
    print(f"    → {path.name}")


def write_summary(all_summaries: list[dict]):
    path = OUT_DIR / "backtest_summary.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "granularity", "steps", "ticker", "mode",
            "mae", "rmse", "mape", "qualite"
        ])
        for row in all_summaries:
            writer.writerow([
                row["granularity"], row["steps"], row["ticker"], row["mode"],
                row["mae"], row["rmse"], row["mape"], row["qualite"]
            ])
    print(f"    → backtest_summary.csv")


def quality(mape: float) -> str:
    if mape < 1:   return "Excellent"
    if mape < 3:   return "Bon"
    if mape < 5:   return "Acceptable"
    if mape < 10:  return "Imprécis"
    return "Mauvais"


def main():
    all_summaries = []
    generated_at  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for gran in GRANULARITIES:
        print(f"\n{'='*55}")
        print(f"  Granularité : {gran}")
        print(f"{'='*55}")

        for steps in HORIZONS:
            print(f"\n  ── {steps} steps ──")
            results = []

            for ticker in TICKERS:
                print(f"    {ticker}...", end=" ", flush=True)
                data = run_one(ticker, steps, gran)
                if data is None:
                    print("ignoré")
                    continue

                mae  = data["metrics"]["mae"]
                rmse = data["metrics"]["rmse"]
                mape = data["metrics"]["mape"]
                q    = quality(mape)
                print(f"MAPE={mape:.4f}%  MAE={mae:.4f}$  [{q}]")

                results.append(data)
                all_summaries.append({
                    "granularity": gran,
                    "steps":       steps,
                    "ticker":      data["ticker"],
                    "mode":        data["prediction_mode"],
                    "mae":         mae,
                    "rmse":        rmse,
                    "mape":        mape,
                    "qualite":     q,
                })

            if results:
                write_detail(results, f"backtest_{gran}_{steps}steps.csv")

    write_summary(all_summaries)

    # ── Résumé console ────────────────────────────────────────────────────────
    print(f"\n{'='*65}")
    print("  RÉSUMÉ PAR GRANULARITÉ ET HORIZON")
    print(f"{'='*65}")
    print(f"  {'Gran':<8} {'Steps':>5}  {'Tickers':>7}  {'MAPE moy':>9}  {'MAPE min':>9}  {'MAPE max':>9}")
    print(f"  {'-'*60}")

    from itertools import groupby
    key = lambda r: (r["granularity"], r["steps"])
    for (gran, steps), group in groupby(sorted(all_summaries, key=key), key=key):
        rows = list(group)
        mapes = [r["mape"] for r in rows]
        best  = min(rows, key=lambda r: r["mape"])
        worst = max(rows, key=lambda r: r["mape"])
        print(
            f"  {gran:<8} {steps:>5}  {len(rows):>7}  "
            f"{sum(mapes)/len(mapes):>8.4f}%  "
            f"{min(mapes):>8.4f}% ({best['ticker']})  "
            f"{max(mapes):>8.4f}% ({worst['ticker']})"
        )

    print(f"\n  Généré le {generated_at}")
    print(f"  Dossier  : {OUT_DIR}")


if __name__ == "__main__":
    main()
