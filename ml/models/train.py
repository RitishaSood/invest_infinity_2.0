"""
models/train.py
────────────────
Trains LSTM and GRU models for each ticker and persists the best weights
plus training history to disk.

Why this file exists
────────────────────
Training orchestration is separate from architecture definitions so the
two concerns can evolve independently.  This module knows *how* to train
(data feeding, callbacks, history serialisation) but is agnostic to what
the model looks like internally — that stays in ``lstm_model.py`` and
``gru_model.py``.

Outputs (per ticker, per model type)
─────────────────────────────────────
  saved_models/lstm/<TICKER>_lstm.keras
  saved_models/gru/<TICKER>_gru.keras
  saved_models/lstm/<TICKER>_lstm_history.json
  saved_models/gru/<TICKER>_gru_history.json
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, Literal, Optional, Tuple

import numpy as np
from tensorflow import keras

from config.config import CFG
from data.dataset_builder import TickerDataset
from models.lstm_model import build_lstm_model, get_lstm_callbacks
from models.gru_model import build_gru_model, get_gru_callbacks

logger = logging.getLogger(__name__)

ModelType = Literal["lstm", "gru"]


# ── Single-model trainer ─────────────────────────────────────────────────────


def train_model(
    model_type: ModelType,
    dataset: TickerDataset,
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    validation_split: float = 0.1,
    saved_models_dir: Optional[Path] = None,
) -> Tuple[keras.Model, dict]:
    """
    Train a single model (LSTM or GRU) on one ticker's dataset.

    Parameters
    ----------
    model_type : "lstm" | "gru"
        Which architecture to train.
    dataset : TickerDataset
        Pre-built dataset from ``dataset_builder.py``.
    epochs : int, optional
        Maximum training epochs.  Defaults to ``CFG.epochs``.
    batch_size : int, optional
        Mini-batch size.  Defaults to ``CFG.batch_size``.
    validation_split : float
        Fraction of training data used for in-training validation
        (used by early stopping and learning-rate scheduler).
        Defaults to ``0.1`` (10 %).
    saved_models_dir : Path, optional
        Root directory for saved weights.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    tuple[keras.Model, dict]
        ``(trained_model, history_dict)`` where ``history_dict`` is a plain
        Python dict of ``{metric_name: [epoch_values, …]}``.
    """
    epochs = epochs or CFG.epochs
    batch_size = batch_size or CFG.batch_size
    saved_models_dir = Path(saved_models_dir) if saved_models_dir else CFG.saved_models_dir

    ticker = dataset.ticker
    input_shape = (dataset.X_train.shape[1], dataset.X_train.shape[2])

    # ── Build model ───────────────────────────────────────────────────────
    if model_type == "lstm":
        model = build_lstm_model(input_shape=input_shape)
        model_save_path = str(
            saved_models_dir / "lstm" / f"{ticker}_lstm.keras"
        )
        callbacks = get_lstm_callbacks(model_save_path)
    else:
        model = build_gru_model(input_shape=input_shape)
        model_save_path = str(
            saved_models_dir / "gru" / f"{ticker}_gru.keras"
        )
        callbacks = get_gru_callbacks(model_save_path)

    # Ensure parent directory exists
    Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)

    # ── Train ─────────────────────────────────────────────────────────────
    logger.info(
        "Training %s for %s  (input=%s, epochs=%d, batch=%d) …",
        model_type.upper(),
        ticker,
        input_shape,
        epochs,
        batch_size,
    )
    t0 = time.time()

    history = model.fit(
        dataset.X_train,
        dataset.y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=callbacks,
        shuffle=False,      # time-series must not be shuffled
        verbose=1,
    )

    elapsed = time.time() - t0
    best_val_loss = min(history.history.get("val_loss", [float("inf")]))
    logger.info(
        "%s [%s] training done in %.1fs — best val_loss=%.6f",
        model_type.upper(),
        ticker,
        elapsed,
        best_val_loss,
    )

    # ── Persist history ───────────────────────────────────────────────────
    history_dict = {k: [float(v) for v in vals] for k, vals in history.history.items()}
    history_path = Path(model_save_path).with_suffix("").with_suffix("") 
    history_path = Path(str(Path(model_save_path).with_suffix("")) + "_history.json")
    _save_json(history_dict, history_path)

    return model, history_dict


# ── Both-models trainer ──────────────────────────────────────────────────────


def train_both_models(
    dataset: TickerDataset,
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    validation_split: float = 0.1,
    saved_models_dir: Optional[Path] = None,
) -> Dict[ModelType, Tuple[keras.Model, dict]]:
    """
    Train both LSTM and GRU for a single ticker and return both results.

    Parameters
    ----------
    dataset : TickerDataset
        Dataset for one ticker.
    epochs : int, optional
        Defaults to ``CFG.epochs``.
    batch_size : int, optional
        Defaults to ``CFG.batch_size``.
    validation_split : float
        In-training validation fraction.  Defaults to ``0.1``.
    saved_models_dir : Path, optional
        Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    dict
        ``{"lstm": (model, history), "gru": (model, history)}``
    """
    results: Dict[ModelType, Tuple[keras.Model, dict]] = {}

    for model_type in ("lstm", "gru"):
        model, history = train_model(
            model_type=model_type,  # type: ignore[arg-type]
            dataset=dataset,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            saved_models_dir=saved_models_dir,
        )
        results[model_type] = (model, history)  # type: ignore[index]

    return results


# ── All-tickers trainer ──────────────────────────────────────────────────────


def train_all_tickers(
    datasets: Dict[str, TickerDataset],
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    validation_split: float = 0.1,
    saved_models_dir: Optional[Path] = None,
) -> Dict[str, Dict[ModelType, Tuple[keras.Model, dict]]]:
    """
    Train LSTM and GRU models for every ticker in *datasets*.

    Failures for individual tickers are caught and logged so one bad ticker
    does not abort the whole training run.

    Parameters
    ----------
    datasets : dict[str, TickerDataset]
        Output of ``dataset_builder.build_all_datasets()``.
    epochs : int, optional
        Defaults to ``CFG.epochs``.
    batch_size : int, optional
        Defaults to ``CFG.batch_size``.
    validation_split : float
        Defaults to ``0.1``.
    saved_models_dir : Path, optional
        Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    dict[str, dict[ModelType, tuple[keras.Model, dict]]]
        Nested mapping: ``ticker → model_type → (model, history)``.
    """
    all_results: Dict[str, Dict[ModelType, Tuple[keras.Model, dict]]] = {}

    for ticker, dataset in datasets.items():
        logger.info("═" * 60)
        logger.info("Training models for %s …", ticker)
        try:
            results = train_both_models(
                dataset=dataset,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                saved_models_dir=saved_models_dir,
            )
            all_results[ticker] = results
        except Exception as exc:
            logger.warning("Skipping %s — training failed: %s", ticker, exc)

    logger.info("═" * 60)
    logger.info(
        "Training complete: %d / %d tickers.", len(all_results), len(datasets)
    )
    return all_results


def load_training_history(
    ticker: str,
    model_type: ModelType,
    saved_models_dir: Optional[Path] = None,
) -> dict:
    """
    Load the JSON training history for a previously trained model.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    model_type : "lstm" | "gru"
        Model architecture.
    saved_models_dir : Path, optional
        Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    dict
        ``{metric_name: [epoch_values, …]}``.

    Raises
    ------
    FileNotFoundError
        If the history file does not exist.
    """
    saved_models_dir = Path(saved_models_dir) if saved_models_dir else CFG.saved_models_dir
    path = saved_models_dir / model_type / f"{ticker}_{model_type}_history.json"
    if not path.exists():
        raise FileNotFoundError(f"Training history not found at {path}.")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    logger.info("History saved → %s", path)


# ── CLI entry-point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import logging
    from data.dataset_builder import build_all_datasets

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    datasets = build_all_datasets()
    train_all_tickers(datasets)