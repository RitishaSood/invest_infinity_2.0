"""
pipelines/training_pipeline.py

Runs the full training pipeline end-to-end for one or more tickers:

    Fetch Data -> Build Dataset (clean + features + scale + split)
    -> Train LSTM -> Train GRU -> Compare Models -> Plot Training Curves

This file only orchestrates - all the real logic lives in the data/,
models/, and evaluation/ modules it calls. If something breaks, the bug
is in one of those modules, not here.
"""

from typing import Dict, List

from config.config import config
from data.dataset_builder import build_dataset
from data.fetch_data import fetch_and_save_all
from evaluation.model_comparison import compare_models, get_better_model
from evaluation.visualization import plot_training_history
from models.train import train_single_model
from utils.logger import get_logger

logger = get_logger(__name__)


def run_training_pipeline(tickers: List[str] = None) -> Dict[str, dict]:
    """
    Execute the full training pipeline for one or more tickers.

    Returns a summary dict: {ticker: {"metrics": {...}, "best_model": "lstm"|"gru"}}
    """
    tickers = tickers or config.tickers
    logger.info(f"Starting training pipeline for: {tickers}")

    fetch_and_save_all(tickers)

    summary: Dict[str, dict] = {}
    for ticker in tickers:
        summary[ticker] = _train_single_ticker(ticker)

    logger.info("Training pipeline complete")
    return summary


def _train_single_ticker(ticker: str) -> dict:
    """Run dataset building, training, evaluation, and plotting for one ticker."""
    logger.info(f"--- Processing {ticker} ---")

    dataset = build_dataset(ticker)
    train_single_model(ticker, "lstm", dataset)
    train_single_model(ticker, "gru", dataset)

    metrics = compare_models(ticker)
    best_model = get_better_model(metrics)
    logger.info(f"{ticker}: best model is {best_model.upper()}")

    plot_training_history(ticker, "lstm")
    plot_training_history(ticker, "gru")

    return {"metrics": metrics, "best_model": best_model}


if __name__ == "__main__":
    run_training_pipeline()