"""
data/feature_engineering.py

Adds technical indicators to raw OHLCV data. These indicators help the
LSTM/GRU models learn patterns beyond the raw closing price.

RSI and MACD are implemented manually with pandas (no extra library
required) - this keeps the dependency list small and makes the math
transparent and easy to explain.
"""

import numpy as np
import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


def add_daily_returns(df: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
    """Add the day-over-day percentage change."""
    df["Daily_Return"] = df[column].pct_change()
    return df


def add_log_returns(df: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
    """Add the log return, which is additive across time (useful for compounding)."""
    df["Log_Return"] = np.log(df[column] / df[column].shift(1))
    return df


def add_moving_averages(df: pd.DataFrame, column: str = "Close", windows: tuple = (20, 50)) -> pd.DataFrame:
    """Add simple moving averages (e.g. MA20, MA50)."""
    for window in windows:
        df[f"MA{window}"] = df[column].rolling(window=window).mean()
    return df


def add_ema(df: pd.DataFrame, column: str = "Close", span: int = 20) -> pd.DataFrame:
    """Add an exponential moving average (reacts faster than a simple MA)."""
    df[f"EMA{span}"] = df[column].ewm(span=span, adjust=False).mean()
    return df


def add_volatility(df: pd.DataFrame, column: str = "Close", window: int = 20) -> pd.DataFrame:
    """Add rolling volatility (standard deviation of price over a window)."""
    df["Volatility"] = df[column].rolling(window=window).std()
    return df


def add_rsi(df: pd.DataFrame, column: str = "Close", window: int = 14) -> pd.DataFrame:
    """Add the Relative Strength Index (momentum indicator, range 0-100)."""
    delta = df[column].diff()

    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)

    avg_gain = gains.rolling(window=window).mean()
    avg_loss = losses.rolling(window=window).mean()

    relative_strength = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + relative_strength))
    return df


def add_macd(df: pd.DataFrame, column: str = "Close", fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Add MACD and its signal line (trend-following momentum indicator)."""
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()

    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    return df


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full feature engineering pipeline in order and drop the
    leading rows that contain NaN values (caused by rolling windows).
    """
    df = df.copy()

    df = add_daily_returns(df)
    df = add_log_returns(df)
    df = add_moving_averages(df)
    df = add_ema(df)
    df = add_volatility(df)
    df = add_rsi(df)
    df = add_macd(df)

    df = df.dropna().reset_index(drop=True)
    logger.info(f"Generated features - final shape: {df.shape}")
    return df