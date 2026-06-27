"""
config/config.py
────────────────
Central configuration for the Invest Infinity ML pipeline.

All tuneable hyper-parameters, paths, and defaults live here so every
other module can import a single `CFG` object instead of scattering
magic numbers across files.  Values are loaded from `settings.yaml` at
import time; the dataclass below acts as the typed schema and supplies
fallback defaults if the YAML key is absent.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


# ── Paths ──────────────────────────────────────────────────────────────────
_ML_ROOT = Path(__file__).resolve().parent.parent          # …/ml/
_SETTINGS_PATH = _ML_ROOT / "config" / "settings.yaml"


# ── Typed configuration schema ──────────────────────────────────────────────
@dataclass
class Config:
    """
    All configurable values for the ML pipeline.

    Attributes
    ----------
    tickers : list[str]
        Stock symbols to download (e.g. ``["AAPL", "MSFT"]``).
    start_date : str
        ISO-8601 date string for the earliest historical price to fetch.
    end_date : str
        ISO-8601 date string for the latest historical price to fetch.
        Defaults to ``"today"`` which is resolved at run time.
    sequence_length : int
        Number of past time-steps fed into each LSTM / GRU window.
    forecast_horizon : int
        How many trading days ahead to predict.
    test_size : float
        Fraction of data held out for evaluation (0 < test_size < 1).
    batch_size : int
        Mini-batch size used during model training.
    epochs : int
        Maximum number of training epochs (early-stopping may end it earlier).
    patience : int
        Early-stopping patience (epochs without improvement before halt).
    lstm_units : list[int]
        Hidden units per LSTM layer (one element per layer).
    gru_units : list[int]
        Hidden units per GRU layer (one element per layer).
    dropout_rate : float
        Dropout probability applied after each recurrent layer.
    learning_rate : float
        Adam optimiser learning rate.
    target_column : str
        The OHLCV column used as the prediction target (default ``"Close"``).
    raw_data_dir : Path
        Where raw CSV files from yfinance are stored.
    saved_models_dir : Path
        Root directory for persisted ``.keras`` weights and scalers.
    metrics_path : Path
        JSON file where evaluation metrics are written.
    """

    # ── Data ─────────────────────────────────────────────────────────────
    tickers: List[str] = field(default_factory=lambda: ["AAPL", "MSFT", "GOOGL"])
    start_date: str = "2018-01-01"
    end_date: str = "today"

    # ── Sequence / forecast ───────────────────────────────────────────────
    sequence_length: int = 60        # look-back window
    forecast_horizon: int = 30       # days ahead to predict

    # ── Train / test split ────────────────────────────────────────────────
    test_size: float = 0.2

    # ── Training hyper-parameters ────────────────────────────────────────
    batch_size: int = 32
    epochs: int = 100
    patience: int = 10               # early-stopping patience
    learning_rate: float = 0.001

    # ── Model architecture ───────────────────────────────────────────────
    lstm_units: List[int] = field(default_factory=lambda: [128, 64])
    gru_units: List[int] = field(default_factory=lambda: [128, 64])
    dropout_rate: float = 0.2

    # ── Target column ─────────────────────────────────────────────────────
    target_column: str = "Close"

    # ── Paths (resolved relative to ml/ root) ────────────────────────────
    raw_data_dir: Path = field(default_factory=lambda: _ML_ROOT / "data" / "raw")
    saved_models_dir: Path = field(default_factory=lambda: _ML_ROOT / "saved_models")
    metrics_path: Path = field(default_factory=lambda: _ML_ROOT / "saved_models" / "metrics.json")


def _load_yaml(path: Path) -> dict:
    """Return the parsed YAML dict, or an empty dict if the file is missing."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config() -> Config:
    """
    Build a :class:`Config` instance by merging ``settings.yaml`` values
    on top of dataclass defaults.

    Returns
    -------
    Config
        Fully populated configuration object.
    """
    raw = _load_yaml(_SETTINGS_PATH)
    cfg = Config()

    # Simple scalar overrides
    for key in (
        "tickers", "start_date", "end_date",
        "sequence_length", "forecast_horizon",
        "test_size", "batch_size", "epochs", "patience", "learning_rate",
        "lstm_units", "gru_units", "dropout_rate",
        "target_column",
    ):
        if key in raw:
            setattr(cfg, key, raw[key])

    # Path overrides — convert str → Path
    for key in ("raw_data_dir", "saved_models_dir", "metrics_path"):
        if key in raw:
            setattr(cfg, key, _ML_ROOT / raw[key])

    # Ensure required directories exist
    os.makedirs(cfg.raw_data_dir, exist_ok=True)
    os.makedirs(cfg.saved_models_dir / "lstm", exist_ok=True)
    os.makedirs(cfg.saved_models_dir / "gru", exist_ok=True)
    os.makedirs(cfg.saved_models_dir / "scalers", exist_ok=True)

    return cfg


# Module-level singleton — import this everywhere
CFG: Config = load_config()