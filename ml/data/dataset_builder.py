"""
data/dataset_builder.py
────────────────────────
Orchestrates the complete data preparation pipeline for all configured
tickers, returning ready-to-train NumPy tensors for LSTM and GRU models.

Why this file exists
────────────────────
``fetch_data``, ``feature_engineering``, and ``preprocess`` each do one
job well.  ``dataset_builder`` is the single place that wires them together
in the correct order: fetch → engineer features → preprocess & scale →
create sequences.  The training and forecasting pipelines call *this* file
rather than constructing the pipeline themselves, keeping duplication to zero.

Public API
──────────
  build_dataset_for_ticker  — full pipeline for one ticker
  build_all_datasets        — runs the above for every ticker in CFG
  TickerDataset             — typed container for a single ticker's tensors
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from config.config import CFG
from data.fetch_data import fetch_ticker, load_ticker_from_csv
from data.feature_engineering import engineer_features, get_feature_columns
from data.preprocess import preprocess_ticker

logger = logging.getLogger(__name__)


# ── Typed result container ───────────────────────────────────────────────────


@dataclass
class TickerDataset:
    """
    All training and evaluation data for a single ticker.

    Attributes
    ----------
    ticker : str
        Stock symbol (e.g. ``"AAPL"``).
    X_train : np.ndarray
        Shape ``(n_train_samples, sequence_length, n_features)``.
    y_train : np.ndarray
        Shape ``(n_train_samples,)`` — scaled target values.
    X_test : np.ndarray
        Shape ``(n_test_samples, sequence_length, n_features)``.
    y_test : np.ndarray
        Shape ``(n_test_samples,)`` — scaled target values.
    scaler : MinMaxScaler
        Fitted scaler; use ``.inverse_transform`` to recover real prices.
    feature_columns : list[str]
        Ordered list of column names corresponding to the last axis of X.
    n_features : int
        Number of input features (= ``X_train.shape[2]``).
    train_df : pd.DataFrame
        The unscaled train split (useful for baseline / plotting).
    test_df : pd.DataFrame
        The unscaled test split.
    """

    ticker: str
    X_train: np.ndarray
    y_train: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    scaler: MinMaxScaler
    feature_columns: List[str] = field(default_factory=list)
    train_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    test_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def n_features(self) -> int:
        """Number of input features (width of the last axis of X_train)."""
        return int(self.X_train.shape[2])

    def summary(self) -> str:
        """Return a one-line description of the dataset."""
        return (
            f"{self.ticker} | "
            f"X_train={self.X_train.shape}  X_test={self.X_test.shape}  "
            f"features={self.n_features}"
        )


# ── Single-ticker pipeline ───────────────────────────────────────────────────


def build_dataset_for_ticker(
    ticker: str,
    use_cache: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sequence_length: Optional[int] = None,
    test_size: Optional[float] = None,
    raw_data_dir: Optional[Path] = None,
) -> TickerDataset:
    """
    Run the full data pipeline for a single ticker and return a
    :class:`TickerDataset`.

    Pipeline
    --------
    1. Load raw CSV from disk (or download from yfinance if not cached).
    2. Engineer all technical-indicator features.
    3. Preprocess: missing values → outlier capping → scale → sequences.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    use_cache : bool
        If ``True`` (default) load from ``raw_data_dir/<ticker>.csv`` when
        available; otherwise always download fresh data.
    start_date : str, optional
        Download start date.  Defaults to ``CFG.start_date``.
    end_date : str, optional
        Download end date.  Defaults to ``CFG.end_date``.
    sequence_length : int, optional
        Look-back window.  Defaults to ``CFG.sequence_length``.
    test_size : float, optional
        Test fraction.  Defaults to ``CFG.test_size``.
    raw_data_dir : Path, optional
        Directory for raw CSV files.  Defaults to ``CFG.raw_data_dir``.

    Returns
    -------
    TickerDataset
    """
    start_date = start_date or CFG.start_date
    end_date = end_date or CFG.end_date
    raw_data_dir = Path(raw_data_dir) if raw_data_dir else CFG.raw_data_dir

    # ── Step 1: Raw data ──────────────────────────────────────────────────
    csv_path = raw_data_dir / f"{ticker}.csv"
    if use_cache and csv_path.exists():
        logger.info("[%s] Loading raw data from cache: %s", ticker, csv_path)
        raw_df = _load_csv(csv_path)
    else:
        logger.info("[%s] Downloading raw data from yfinance …", ticker)
        raw_df = fetch_ticker(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            save_dir=raw_data_dir,
        )

    # ── Step 2: Feature engineering ───────────────────────────────────────
    logger.info("[%s] Engineering features …", ticker)
    featured_df = engineer_features(raw_df)
    feature_cols = get_feature_columns(featured_df)

    # ── Step 3: Preprocess → tensors ──────────────────────────────────────
    logger.info("[%s] Preprocessing and building sequences …", ticker)
    result = preprocess_ticker(
        df=featured_df,
        ticker=ticker,
        feature_columns=feature_cols,
        sequence_length=sequence_length,
        test_size=test_size,
    )

    dataset = TickerDataset(
        ticker=ticker,
        X_train=result["X_train"],
        y_train=result["y_train"],
        X_test=result["X_test"],
        y_test=result["y_test"],
        scaler=result["scaler"],
        feature_columns=feature_cols,
        train_df=result["train_df"],
        test_df=result["test_df"],
    )

    logger.info("[%s] Dataset ready. %s", ticker, dataset.summary())
    return dataset


# ── Multi-ticker pipeline ────────────────────────────────────────────────────


def build_all_datasets(
    tickers: Optional[List[str]] = None,
    use_cache: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sequence_length: Optional[int] = None,
    test_size: Optional[float] = None,
) -> Dict[str, TickerDataset]:
    """
    Build :class:`TickerDataset` objects for every ticker in *tickers*.

    Tickers that fail (network error, insufficient history, etc.) are logged
    as warnings and excluded from the returned dict so the rest of the run
    can proceed.

    Parameters
    ----------
    tickers : list[str], optional
        Defaults to ``CFG.tickers``.
    use_cache : bool
        Whether to use cached CSVs when available.
    start_date : str, optional
        Defaults to ``CFG.start_date``.
    end_date : str, optional
        Defaults to ``CFG.end_date``.
    sequence_length : int, optional
        Defaults to ``CFG.sequence_length``.
    test_size : float, optional
        Defaults to ``CFG.test_size``.

    Returns
    -------
    dict[str, TickerDataset]
        Mapping of ``ticker → TickerDataset`` for successful tickers.
    """
    tickers = tickers or CFG.tickers
    datasets: Dict[str, TickerDataset] = {}

    for ticker in tickers:
        try:
            ds = build_dataset_for_ticker(
                ticker=ticker,
                use_cache=use_cache,
                start_date=start_date,
                end_date=end_date,
                sequence_length=sequence_length,
                test_size=test_size,
            )
            datasets[ticker] = ds
        except Exception as exc:
            logger.warning(
                "Skipping %s — dataset build failed: %s", ticker, exc
            )

    logger.info(
        "Datasets built: %d / %d tickers succeeded.",
        len(datasets),
        len(tickers),
    )
    return datasets


def get_dataset_info(datasets: Dict[str, TickerDataset]) -> pd.DataFrame:
    """
    Return a summary DataFrame describing all built datasets.

    Useful for a quick sanity-check before training.

    Parameters
    ----------
    datasets : dict[str, TickerDataset]
        Output of :func:`build_all_datasets`.

    Returns
    -------
    pd.DataFrame
        One row per ticker with columns: ticker, n_train, n_test,
        sequence_length, n_features.
    """
    rows = []
    for ticker, ds in datasets.items():
        rows.append(
            {
                "ticker": ticker,
                "n_train_samples": len(ds.X_train),
                "n_test_samples": len(ds.X_test),
                "sequence_length": ds.X_train.shape[1],
                "n_features": ds.n_features,
            }
        )
    return pd.DataFrame(rows).set_index("ticker")


# ── Helpers ──────────────────────────────────────────────────────────────────


def _load_csv(path: Path) -> pd.DataFrame:
    """Load a raw OHLCV CSV saved by ``fetch_data.py``."""
    df = pd.read_csv(path, index_col="Date", parse_dates=True)
    return df[["Open", "High", "Low", "Close", "Volume"]].copy()


# ── CLI entry-point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    all_ds = build_all_datasets()
    print("\n── Dataset Summary ──────────────────────────────────")
    print(get_dataset_info(all_ds).to_string())