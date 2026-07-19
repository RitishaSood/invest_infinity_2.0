"""
models/train.py

Trains LSTM and GRU models for one or more tickers and saves:
- The trained .keras model files
- Their per-epoch training history as JSON

Scalers are already saved by data/dataset_builder.py, so this file only
deals with building, training, and persisting the models themselves.
"""

import json
from pathlib import Path
from typing import Dict, List, Literal

from config.config import config
from data.dataset_builder import build_dataset
from models.gru_model import build_gru_model
from models.gru_model import get_early_stopping_callback as get_gru_early_stopping
from models.lstm_model import build_lstm_model
from models.lstm_model import get_early_stopping_callback as get_lstm_early_stopping
from utils.logger import get_logger

logger = get_logger(__name__)

ModelType = Literal["lstm", "gru"]


def _get_model_save_path(ticker: str, model_type: ModelType) -> Path:
    """Return where a trained model should be saved (must match model_loader.py)."""
    model_dir = config.lstm_model_dir if model_type == "lstm" else config.gru_model_dir
    return model_dir / f"{ticker}_{model_type}.keras"


def _get_history_save_path(ticker: str, model_type: ModelType) -> Path:
    """Return where a model's training history JSON should be saved."""
    model_dir = config.lstm_model_dir if model_type == "lstm" else config.gru_model_dir
    return model_dir / f"{ticker}_{model_type}_history.json"


def save_training_history(history: dict, ticker: str, model_type: ModelType) -> Path:
    """Save a model's per-epoch loss/mae history to disk as JSON."""
    history_path = _get_history_save_path(ticker, model_type)
    with open(history_path, "w") as file:
        json.dump(history, file, indent=2)
    logger.info(f"Saved training history for {ticker} ({model_type}) to {history_path}")
    return history_path


def train_single_model(ticker: str, model_type: ModelType, dataset: dict) -> Dict[str, list]:
    """
    Train one model (LSTM or GRU) for a single ticker on a prebuilt dataset.

    Saves the trained model to disk and returns its training history
    (a dict of lists, one entry per epoch, e.g. {"loss": [...], "val_loss": [...]}).
    """
    input_shape = (dataset["X_train"].shape[1], dataset["X_train"].shape[2])

    if model_type == "lstm":
        model = build_lstm_model(input_shape)
        early_stopping = get_lstm_early_stopping()
    else:
        model = build_gru_model(input_shape)
        early_stopping = get_gru_early_stopping()

    logger.info(f"Training {model_type.upper()} model for {ticker}")
    result = model.fit(
        dataset["X_train"],
        dataset["y_train"],
        validation_data=(dataset["X_test"], dataset["y_test"]),
        epochs=config.epochs,
        batch_size=config.batch_size,
        callbacks=[early_stopping],
        verbose=0,
    )

    model_path = _get_model_save_path(ticker, model_type)
    model.save(model_path)
    logger.info(f"Saved {model_type.upper()} model for {ticker} to {model_path}")

    # Convert numpy floats to plain floats so the history is JSON serializable.
    history = {key: [float(v) for v in values] for key, values in result.history.items()}
    save_training_history(history, ticker, model_type)

    return history


def train_all_models(tickers: List[str] = None) -> Dict[str, Dict[str, dict]]:
    """
    Train both LSTM and GRU models for every ticker.

    Returns a nested dict: {ticker: {"lstm": history, "gru": history}}
    """
    tickers = tickers or config.tickers
    all_histories: Dict[str, Dict[str, dict]] = {}

    for ticker in tickers:
        dataset = build_dataset(ticker)
        lstm_history = train_single_model(ticker, "lstm", dataset)
        gru_history = train_single_model(ticker, "gru", dataset)
        all_histories[ticker] = {"lstm": lstm_history, "gru": gru_history}

    return all_histories


if __name__ == "__main__":
    train_all_models()