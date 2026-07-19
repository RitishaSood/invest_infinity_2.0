"""
evaluation/model_comparison.py

Compares LSTM and GRU models for a given ticker side by side, using the
same backtest logic from backtesting.py so there's only one place in the
project that knows how to "run a model on the test set".
"""

import json
from pathlib import Path
from typing import Dict

from config.config import config
from evaluation.backtesting import run_backtest
from utils.logger import get_logger

logger = get_logger(__name__)


def compare_models(ticker: str) -> Dict[str, dict]:
    """
    Evaluate both LSTM and GRU models for a ticker on the same test set
    and return their metrics side by side.
    """
    comparison: Dict[str, dict] = {}

    for model_type in ("lstm", "gru"):
        result = run_backtest(ticker, model_type)
        comparison[model_type] = result["metrics"]

    save_comparison(comparison, ticker)
    return comparison


def save_comparison(comparison: dict, ticker: str) -> Path:
    """Save the LSTM vs GRU comparison to <ticker>_metrics.json."""
    metrics_path = config.saved_models_dir / f"{ticker}_metrics.json"

    with open(metrics_path, "w") as file:
        json.dump(comparison, file, indent=2)

    logger.info(f"Saved model comparison for {ticker} to {metrics_path}")
    return metrics_path


def get_better_model(comparison: Dict[str, dict], metric: str = "rmse") -> str:
    """Return whichever model ('lstm' or 'gru') scored lower on the given metric."""
    if comparison["lstm"][metric] <= comparison["gru"][metric]:
        return "lstm"
    return "gru"


if __name__ == "__main__":
    for ticker in config.tickers:
        result = compare_models(ticker)
        best = get_better_model(result)
        logger.info(f"{ticker}: best model is {best.upper()}")