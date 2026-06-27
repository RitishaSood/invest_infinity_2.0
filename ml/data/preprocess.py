"""
data/preprocess.py
──────────────────
Cleans raw OHLCV DataFrames and converts them into the scaled, windowed
NumPy arrays that the LSTM / GRU models consume.

Why this file exists
────────────────────
Raw market data contains gaps (weekends, holidays, corporate actions) and
occasional outlier spikes.  Neural networks are sensitive to unscaled inputs,
so every feature column must be normalised to [0, 1] before training.
Separating these concerns from feature engineering keeps each module focused
and testable in isolation.

Pipeline (in order)
───────────────────
1. ``handle_missing_values``  — forward-fill then drop any remaining NaNs
2. ``handle_outliers``        — IQR-based capping per column
3. ``scale_features``         — MinMaxScaler fitted on train split only
4. ``train_test_split_df``    — chronological split (no shuffle)
5. ``create_sequences``       — sliding-window → (X, y) tensors
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from config.config import CFG

logger = logging.getLogger(__name__)


# ── 1. Missing value handling ────────────────────────────────────────────────


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in *df* using forward-fill then drop any residual NaNs.

    Stock price data has no values on weekends / public holidays so a simple
    ``ffill`` propagates the last known price, which is the standard convention
    in quantitative finance.

    Parameters
    ----------
    df : pd.DataFrame
        Raw OHLCV DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with no NaN values.
    """
    before = df.isna().sum().sum()
    df = df.ffill().bfill()
    after = df.isna().sum().sum()
    dropped = before - after
    if dropped:
        logger.info("Missing values filled: %d cells affected.", dropped)
    df = df.dropna()
    return df


# ── 2. Outlier handling ──────────────────────────────────────────────────────


def handle_outliers(
    df: pd.DataFrame,
    iqr_factor: float = 3.0,
    columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Cap extreme values using the IQR (interquartile range) method.

    Values beyond ``Q1 - factor * IQR`` or ``Q3 + factor * IQR`` are clipped
    to those bounds.  This preserves the row count (no deletion) while
    preventing a handful of corporate-action spikes from dominating the loss.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    iqr_factor : float
        Multiplier applied to IQR for computing bounds (default ``3.0``).
    columns : list[str], optional
        Columns to inspect.  Defaults to all numeric columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with extreme values clipped.
    """
    df = df.copy()
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()

    for col in cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - iqr_factor * iqr
        upper = q3 + iqr_factor * iqr
        clipped = ((df[col] < lower) | (df[col] > upper)).sum()
        if clipped:
            logger.debug("Clipping %d outliers in '%s'.", clipped, col)
        df[col] = df[col].clip(lower, upper)

    return df


# ── 3. Train / test split ────────────────────────────────────────────────────


def train_test_split_df(
    df: pd.DataFrame,
    test_size: Optional[float] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split *df* chronologically into train and test sets.

    No shuffling is applied — time-series data must keep temporal order so
    the model never "sees the future" during training.

    Parameters
    ----------
    df : pd.DataFrame
        Full feature DataFrame sorted by date.
    test_size : float, optional
        Fraction of rows for the test split.  Defaults to ``CFG.test_size``.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        ``(train_df, test_df)``
    """
    test_size = test_size if test_size is not None else CFG.test_size
    split_idx = int(len(df) * (1 - test_size))
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    logger.info(
        "Train/test split: %d train rows, %d test rows (%.0f%% / %.0f%%)",
        len(train_df),
        len(test_df),
        (1 - test_size) * 100,
        test_size * 100,
    )
    return train_df, test_df


# ── 4. Feature scaling ───────────────────────────────────────────────────────


def scale_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    ticker: str,
    feature_columns: Optional[list[str]] = None,
    save_dir: Optional[Path] = None,
) -> Tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    """
    Fit a MinMaxScaler on *train_df* and transform both splits.

    The scaler is fitted **only on training data** to prevent data leakage.
    It is then saved to disk so the forecasting pipeline can inverse-transform
    model outputs back to actual price values.

    Parameters
    ----------
    train_df : pd.DataFrame
        Training split DataFrame.
    test_df : pd.DataFrame
        Test split DataFrame.
    ticker : str
        Ticker symbol used to name the saved scaler file.
    feature_columns : list[str], optional
        Columns to scale.  Defaults to all numeric columns in *train_df*.
    save_dir : Path, optional
        Directory to save ``<ticker>_scaler.joblib``.
        Defaults to ``CFG.saved_models_dir / "scalers"``.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, MinMaxScaler]
        ``(train_scaled, test_scaled, scaler)``
    """
    save_dir = Path(save_dir) if save_dir else CFG.saved_models_dir / "scalers"
    save_dir.mkdir(parents=True, exist_ok=True)

    cols = feature_columns or train_df.select_dtypes(include=[np.number]).columns.tolist()

    scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled: np.ndarray = scaler.fit_transform(train_df[cols].values)
    test_scaled: np.ndarray = scaler.transform(test_df[cols].values)

    scaler_path = save_dir / f"{ticker}_scaler.joblib"
    joblib.dump(scaler, scaler_path)
    logger.info("Scaler saved → %s", scaler_path)

    return train_scaled, test_scaled, scaler


def load_scaler(ticker: str, save_dir: Optional[Path] = None) -> MinMaxScaler:
    """
    Load a previously fitted scaler from disk.

    Parameters
    ----------
    ticker : str
        Ticker symbol.
    save_dir : Path, optional
        Directory containing ``<ticker>_scaler.joblib``.

    Returns
    -------
    MinMaxScaler

    Raises
    ------
    FileNotFoundError
        If the scaler file does not exist.
    """
    save_dir = Path(save_dir) if save_dir else CFG.saved_models_dir / "scalers"
    path = save_dir / f"{ticker}_scaler.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Scaler not found at {path}. Train the model first.")
    scaler: MinMaxScaler = joblib.load(path)
    logger.info("Scaler loaded ← %s", path)
    return scaler


# ── 5. Sequence generation ───────────────────────────────────────────────────


def create_sequences(
    data: np.ndarray,
    sequence_length: Optional[int] = None,
    target_col_index: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert a scaled 2-D array into sliding-window (X, y) pairs.

    Each sample ``X[i]`` is a window of ``sequence_length`` consecutive rows;
    the corresponding label ``y[i]`` is the value of ``target_col_index`` in
    the very next row (one-step ahead prediction).

    Parameters
    ----------
    data : np.ndarray
        Scaled 2-D array of shape ``(n_timesteps, n_features)``.
    sequence_length : int, optional
        Look-back window size.  Defaults to ``CFG.sequence_length``.
    target_col_index : int
        Column index of the target variable (typically ``Close`` == 0 after
        the feature matrix is constructed with Close first).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        ``X`` shape ``(n_samples, sequence_length, n_features)``
        ``y`` shape ``(n_samples,)``
    """
    seq_len = sequence_length or CFG.sequence_length
    X, y = [], []

    for i in range(seq_len, len(data)):
        X.append(data[i - seq_len : i, :])           # full feature window
        y.append(data[i, target_col_index])           # next-step target

    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=np.float32)

    logger.info(
        "Sequences created: X=%s  y=%s",
        X_arr.shape,
        y_arr.shape,
    )
    return X_arr, y_arr


# ── Convenience wrapper ──────────────────────────────────────────────────────


def preprocess_ticker(
    df: pd.DataFrame,
    ticker: str,
    feature_columns: Optional[list[str]] = None,
    sequence_length: Optional[int] = None,
    test_size: Optional[float] = None,
) -> dict:
    """
    Run the full preprocessing pipeline for a single ticker.

    Steps: missing values → outlier capping → train/test split →
    scaling → sequence generation.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered DataFrame (output of ``feature_engineering.py``).
    ticker : str
        Ticker symbol (used for scaler file naming).
    feature_columns : list[str], optional
        Columns to include.  Defaults to all numeric columns.
    sequence_length : int, optional
        Look-back window.  Defaults to ``CFG.sequence_length``.
    test_size : float, optional
        Test fraction.  Defaults to ``CFG.test_size``.

    Returns
    -------
    dict with keys:
        ``X_train``, ``y_train``, ``X_test``, ``y_test``,
        ``scaler``, ``train_df``, ``test_df``
    """
    df = handle_missing_values(df)
    df = handle_outliers(df)

    train_df, test_df = train_test_split_df(df, test_size=test_size)

    cols = feature_columns or df.select_dtypes(include=[np.number]).columns.tolist()
    train_scaled, test_scaled, scaler = scale_features(
        train_df, test_df, ticker=ticker, feature_columns=cols
    )

    # Identify the target column index within the selected columns
    target_col = CFG.target_column
    target_idx = cols.index(target_col) if target_col in cols else 0

    X_train, y_train = create_sequences(train_scaled, sequence_length, target_idx)
    X_test, y_test = create_sequences(test_scaled, sequence_length, target_idx)

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "scaler": scaler,
        "train_df": train_df,
        "test_df": test_df,
        "feature_columns": cols,
        "target_col_index": target_idx,
    }