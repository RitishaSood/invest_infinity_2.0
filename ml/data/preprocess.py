"""
data/preprocess.py

Cleans raw stock data and prepares it for modeling:
- Handles missing values
- Handles outliers
- Scales data with Min-Max scaling
- Splits data into train/test sets
- Builds sliding-window sequences for LSTM/GRU input
"""

from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from utils.logger import get_logger

logger = get_logger(__name__)


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values using forward-fill, then backward-fill as a fallback."""
    df = df.copy()
    missing_before = int(df.isna().sum().sum())

    df = df.ffill().bfill()

    logger.info(f"Handled {missing_before} missing values")
    return df


def handle_outliers(df: pd.DataFrame, column: str = "Close", z_thresh: float = 3.0) -> pd.DataFrame:
    """Clip extreme outliers in a column using the z-score method."""
    df = df.copy()

    mean = df[column].mean()
    std = df[column].std()
    z_scores = (df[column] - mean) / std

    lower_bound = mean - z_thresh * std
    upper_bound = mean + z_thresh * std
    outlier_count = int((z_scores.abs() > z_thresh).sum())

    df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)

    logger.info(f"Clipped {outlier_count} outliers in '{column}'")
    return df


def scale_data(df: pd.DataFrame, feature_columns: List[str]) -> Tuple[np.ndarray, MinMaxScaler]:
    """Scale selected feature columns to the [0, 1] range using MinMaxScaler."""
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_values = scaler.fit_transform(df[feature_columns])
    return scaled_values, scaler


def train_test_split_series(data: np.ndarray, split_ratio: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Split a time-ordered array into train/test sets without shuffling.

    Time series data must stay in order - shuffling would leak future
    information into the training set.
    """
    split_index = int(len(data) * split_ratio)
    train_data = data[:split_index]
    test_data = data[split_index:]
    return train_data, test_data


def create_sequences(
    data: np.ndarray,
    sequence_length: int,
    target_column_index: int = 0,
    forecast_horizon: int = 1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert a 2D array into sliding-window sequences for LSTM/GRU models.

    Each input sample (X) is `sequence_length` time steps of all features.
    Each target (y) is the value of `target_column_index`, `forecast_horizon`
    steps after the input window ends.

    Example: sequence_length=60, forecast_horizon=1 means "use the last
    60 days to predict tomorrow's price".
    """
    X, y = [], []

    last_valid_start = len(data) - sequence_length - forecast_horizon + 1
    for i in range(last_valid_start):
        window = data[i : i + sequence_length]
        target = data[i + sequence_length + forecast_horizon - 1, target_column_index]
        X.append(window)
        y.append(target)

    return np.array(X), np.array(y)