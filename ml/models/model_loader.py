"""
models/model_loader.py
───────────────────────
Loads persisted ``.keras`` model weights and ``joblib`` scalers from disk,
providing a clean interface for the prediction and evaluation modules.

Why this file exists
────────────────────
Loading logic is needed in three separate places: ``predict.py``,
``evaluation/``, and the FastAPI routes.  Centralising it here means that
if the save-path convention ever changes, only this file needs updating.
It also provides consistent error messages when a model hasn't been trained
yet — a common stumbling block in development.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras

from config.config import CFG

logger = logging.getLogger(__name__)

# ── Type alias ──────────────────────────────────────────────────────────────
ModelType = str   # "lstm" | "gru"


# ── Path helpers ─────────────────────────────────────────────────────────────


def get_model_path(
    ticker: str,
    model_type: ModelType,
    saved_models_dir: Optional[Path] = None,
) -> Path:
    """
    Return the canonical ``.keras`` file path for *ticker* / *model_type*.

    Parameters
    ----------
    ticker : str
        Stock symbol (e.g. ``"AAPL"``).
    model_type : str
        ``"lstm"`` or ``"gru"``.
    saved_models_dir : Path, optional
        Root directory.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    Path
    """
    saved_models_dir = Path(saved_models_dir) if saved_models_dir else CFG.saved_models_dir
    return saved_models_dir / model_type / f"{ticker}_{model_type}.keras"


def get_scaler_path(
    ticker: str,
    saved_models_dir: Optional[Path] = None,
) -> Path:
    """
    Return the canonical scaler file path for *ticker*.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    saved_models_dir : Path, optional
        Root directory.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    Path
    """
    saved_models_dir = Path(saved_models_dir) if saved_models_dir else CFG.saved_models_dir
    return saved_models_dir / "scalers" / f"{ticker}_scaler.joblib"


# ── Loaders ──────────────────────────────────────────────────────────────────


def load_model(
    ticker: str,
    model_type: ModelType,
    saved_models_dir: Optional[Path] = None,
) -> keras.Model:
    """
    Load a trained Keras model from disk.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    model_type : str
        ``"lstm"`` or ``"gru"``.
    saved_models_dir : Path, optional
        Root directory.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    keras.Model
        The loaded model with all weights restored.

    Raises
    ------
    FileNotFoundError
        If the model file does not exist (i.e. training has not run yet).
    """
    path = get_model_path(ticker, model_type, saved_models_dir)

    if not path.exists():
        raise FileNotFoundError(
            f"No trained {model_type.upper()} model found for '{ticker}' at:\n"
            f"  {path}\n"
            "Run the training pipeline first."
        )

    model: keras.Model = keras.models.load_model(str(path))
    logger.info("Model loaded ← %s", path)
    return model


def load_scaler(
    ticker: str,
    saved_models_dir: Optional[Path] = None,
) -> MinMaxScaler:
    """
    Load the fitted MinMaxScaler for *ticker* from disk.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    saved_models_dir : Path, optional
        Root directory.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    MinMaxScaler

    Raises
    ------
    FileNotFoundError
        If the scaler file does not exist.
    """
    path = get_scaler_path(ticker, saved_models_dir)

    if not path.exists():
        raise FileNotFoundError(
            f"No scaler found for '{ticker}' at:\n"
            f"  {path}\n"
            "Run the training pipeline first."
        )

    scaler: MinMaxScaler = joblib.load(path)
    logger.info("Scaler loaded ← %s", path)
    return scaler


def load_model_and_scaler(
    ticker: str,
    model_type: ModelType,
    saved_models_dir: Optional[Path] = None,
) -> Tuple[keras.Model, MinMaxScaler]:
    """
    Convenience wrapper — load both model and scaler in one call.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    model_type : str
        ``"lstm"`` or ``"gru"``.
    saved_models_dir : Path, optional
        Root directory.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    tuple[keras.Model, MinMaxScaler]
        ``(model, scaler)``
    """
    model = load_model(ticker, model_type, saved_models_dir)
    scaler = load_scaler(ticker, saved_models_dir)
    return model, scaler


# ── Availability checks ──────────────────────────────────────────────────────


def model_exists(
    ticker: str,
    model_type: ModelType,
    saved_models_dir: Optional[Path] = None,
) -> bool:
    """
    Return ``True`` if a trained model file exists for *ticker* / *model_type*.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    model_type : str
        ``"lstm"`` or ``"gru"``.
    saved_models_dir : Path, optional
        Root directory.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    bool
    """
    return get_model_path(ticker, model_type, saved_models_dir).exists()


def scaler_exists(
    ticker: str,
    saved_models_dir: Optional[Path] = None,
) -> bool:
    """
    Return ``True`` if a scaler file exists for *ticker*.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    saved_models_dir : Path, optional
        Root directory.  Defaults to ``CFG.saved_models_dir``.

    Returns
    -------
    bool
    """
    return get_scaler_path(ticker, saved_models_dir).exists()


def list_trained_models(
    saved_models_dir: Optional[Path] = None,
) -> dict[str, list[str]]:
    """
    Scan the saved-models directory and return which models are trained.

    Returns
    -------
    dict[str, list[str]]
        ``{"AAPL": ["lstm", "gru"], "MSFT": ["lstm"], …}``
    """
    saved_models_dir = Path(saved_models_dir) if saved_models_dir else CFG.saved_models_dir
    trained: dict[str, list[str]] = {}

    for model_type in ("lstm", "gru"):
        model_dir = saved_models_dir / model_type
        if not model_dir.exists():
            continue
        for keras_file in model_dir.glob("*.keras"):
            # filename pattern: <TICKER>_<model_type>.keras
            ticker = keras_file.stem.replace(f"_{model_type}", "")
            trained.setdefault(ticker, []).append(model_type)

    return trained