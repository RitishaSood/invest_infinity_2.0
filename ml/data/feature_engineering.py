"""
data/feature_engineering.py
────────────────────────────
Computes technical indicators and derived price features on top of raw
OHLCV data, returning an enriched DataFrame ready for preprocessing.

Why this file exists
────────────────────
Raw price and volume columns alone give an LSTM / GRU very little signal.
Adding momentum, trend, and volatility indicators as extra input features
(channels) is standard practice in financial forecasting and consistently
improves model accuracy.  Keeping all indicator logic here makes it trivial
to add or remove features without touching the model code.

Features generated
──────────────────
  Daily Returns     — percentage change of Close day-over-day
  Log Returns       — natural log of (Close_t / Close_{t-1})
  MA20              — 20-day Simple Moving Average of Close
  MA50              — 50-day Simple Moving Average of Close
  EMA20             — 20-day Exponential Moving Average of Close
  Volatility20      — 20-day rolling standard deviation of Log Returns
  RSI14             — 14-period Relative Strength Index
  MACD              — 12-26 EMA difference
  MACD_Signal       — 9-period EMA of MACD
  MACD_Histogram    — MACD − Signal
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ── Individual indicator functions ───────────────────────────────────────────


def add_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a ``Daily_Return`` column: percentage change of ``Close``.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``Close`` column.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with ``Daily_Return`` appended.
    """
    df = df.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    return df


def add_log_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a ``Log_Return`` column: ``ln(Close_t / Close_{t-1})``.

    Log returns are approximately normally distributed for short intervals
    and are additive over time — useful properties for financial models.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``Close`` column.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with ``Log_Return`` appended.
    """
    df = df.copy()
    df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))
    return df


def add_moving_averages(
    df: pd.DataFrame,
    windows: Optional[list[int]] = None,
) -> pd.DataFrame:
    """
    Add Simple Moving Average columns for each window size.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``Close`` column.
    windows : list[int], optional
        Rolling window sizes in trading days.  Defaults to ``[20, 50]``.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with ``MA<window>`` columns appended.
    """
    df = df.copy()
    windows = windows or [20, 50]
    for w in windows:
        df[f"MA{w}"] = df["Close"].rolling(window=w).mean()
    return df


def add_ema(
    df: pd.DataFrame,
    windows: Optional[list[int]] = None,
) -> pd.DataFrame:
    """
    Add Exponential Moving Average columns for each window size.

    EMA gives more weight to recent prices, making it more responsive to
    new information than a simple moving average.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``Close`` column.
    windows : list[int], optional
        Span values in trading days.  Defaults to ``[20]``.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with ``EMA<window>`` columns appended.
    """
    df = df.copy()
    windows = windows or [20]
    for w in windows:
        df[f"EMA{w}"] = df["Close"].ewm(span=w, adjust=False).mean()
    return df


def add_volatility(
    df: pd.DataFrame,
    window: int = 20,
) -> pd.DataFrame:
    """
    Add a rolling annualised volatility column based on log returns.

    Volatility = rolling std of Log_Return × √252  (annualised).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``Log_Return`` column (added by :func:`add_log_returns`).
    window : int
        Rolling window in trading days.  Defaults to ``20``.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with ``Volatility{window}`` appended.
    """
    df = df.copy()
    if "Log_Return" not in df.columns:
        df = add_log_returns(df)
    df[f"Volatility{window}"] = (
        df["Log_Return"].rolling(window=window).std() * np.sqrt(252)
    )
    return df


def add_rsi(
    df: pd.DataFrame,
    period: int = 14,
) -> pd.DataFrame:
    """
    Add the Relative Strength Index (RSI) using the Wilder smoothing method.

    RSI oscillates between 0 and 100.  Values above 70 conventionally signal
    overbought conditions; below 30 signal oversold.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``Close`` column.
    period : int
        Look-back period in trading days.  Defaults to ``14``.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with ``RSI{period}`` appended.
    """
    df = df.copy()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df[f"RSI{period}"] = 100 - (100 / (1 + rs))
    return df


def add_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    Add MACD, Signal line, and Histogram columns.

    MACD = EMA(fast) − EMA(slow)
    Signal = EMA(MACD, signal_period)
    Histogram = MACD − Signal

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``Close`` column.
    fast : int
        Fast EMA span.  Defaults to ``12``.
    slow : int
        Slow EMA span.  Defaults to ``26``.
    signal : int
        Signal EMA span.  Defaults to ``9``.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with ``MACD``, ``MACD_Signal``, ``MACD_Histogram``
        columns appended.
    """
    df = df.copy()
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]
    return df


# ── Master pipeline ──────────────────────────────────────────────────────────


def engineer_features(
    df: pd.DataFrame,
    ma_windows: Optional[list[int]] = None,
    ema_windows: Optional[list[int]] = None,
    volatility_window: int = 20,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    drop_na: bool = True,
) -> pd.DataFrame:
    """
    Apply the full feature-engineering pipeline to a raw OHLCV DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw OHLCV data with a ``DatetimeIndex``.
    ma_windows : list[int], optional
        SMA windows.  Defaults to ``[20, 50]``.
    ema_windows : list[int], optional
        EMA spans.  Defaults to ``[20]``.
    volatility_window : int
        Rolling window for volatility.  Defaults to ``20``.
    rsi_period : int
        RSI look-back period.  Defaults to ``14``.
    macd_fast : int
        MACD fast EMA span.  Defaults to ``12``.
    macd_slow : int
        MACD slow EMA span.  Defaults to ``26``.
    macd_signal : int
        MACD signal EMA span.  Defaults to ``9``.
    drop_na : bool
        If ``True`` (default) drop rows with NaN values that arise from
        rolling windows at the start of the series.

    Returns
    -------
    pd.DataFrame
        Enriched DataFrame containing the original OHLCV columns plus all
        computed technical indicators.
    """
    df = df.copy()

    df = add_daily_returns(df)
    df = add_log_returns(df)
    df = add_moving_averages(df, windows=ma_windows or [20, 50])
    df = add_ema(df, windows=ema_windows or [20])
    df = add_volatility(df, window=volatility_window)
    df = add_rsi(df, period=rsi_period)
    df = add_macd(df, fast=macd_fast, slow=macd_slow, signal=macd_signal)

    if drop_na:
        before = len(df)
        df = df.dropna()
        dropped = before - len(df)
        if dropped:
            logger.info(
                "Dropped %d rows with NaN (warm-up period for rolling indicators).",
                dropped,
            )

    logger.info(
        "Feature engineering complete: %d rows × %d columns",
        len(df),
        len(df.columns),
    )
    logger.debug("Columns: %s", df.columns.tolist())
    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """
    Return the list of numeric columns in *df* in the canonical order used
    by the preprocessing and dataset-builder steps.

    The ``Close`` column is always placed first so that
    ``target_col_index=0`` in :func:`~data.preprocess.create_sequences`
    is always correct.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered DataFrame.

    Returns
    -------
    list[str]
        Column names starting with ``Close``, followed by the rest.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Ensure Close is first
    if "Close" in numeric_cols:
        numeric_cols = ["Close"] + [c for c in numeric_cols if c != "Close"]
    return numeric_cols