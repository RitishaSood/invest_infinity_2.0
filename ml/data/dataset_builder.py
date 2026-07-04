"""
data/dataset_builder.py

Combines preprocessing and feature engineering into ready-to-train NumPy
tensors. LSTM and GRU both consume the same tensor shape
(samples, sequence_length, num_features), so this single builder is
reused for both models - there's no need for separate LSTM/GRU builders.
"""

from typing import Dict, List

import joblib

from config.config import config
from data.feature_engineering import generate_features
from data.fetch_data import load_raw_data
from data.preprocess import (
    create_sequences,
    handle_missing_values,
    handle_outliers,
    scale_data,
    train_test_split_series,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Feature columns used as model input. "Close" must stay at index 0 - it
# doubles as the prediction target in create_sequences() below.
FEATURE_COLUMNS: List[str] = [
    "Close",
    "Daily_Return",
    "MA20",
    "MA50",
    "EMA20",
    "Volatility",
    "RSI",
    "MACD",
]


def build_dataset(ticker: str) -> Dict[str, object]:
    """
    Build a complete train/test dataset for a single ticker.

    Pipeline: load raw CSV -> clean -> engineer features -> scale ->
    split into train/test -> build sliding-window sequences.

    The train/test split happens BEFORE sequence creation so that no
    sequence window straddles the split boundary (this avoids leaking
    test data into training).

    Returns a dict with X_train, X_test, y_train, y_test, the fitted
    scaler, and the feature column names (needed later by predict.py).
    """
    logger.info(f"Building dataset for {ticker}")

    raw_df = load_raw_data(ticker)
    clean_df = handle_missing_values(raw_df)
    clean_df = handle_outliers(clean_df)
    featured_df = generate_features(clean_df)

    scaled_values, scaler = scale_data(featured_df, FEATURE_COLUMNS)
    train_raw, test_raw = train_test_split_series(scaled_values, config.train_test_split)

    X_train, y_train = create_sequences(
        train_raw, sequence_length=config.sequence_length, target_column_index=0
    )
    X_test, y_test = create_sequences(
        test_raw, sequence_length=config.sequence_length, target_column_index=0
    )

    save_scaler(scaler, ticker)

    logger.info(
        f"{ticker} dataset ready - X_train: {X_train.shape}, X_test: {X_test.shape}"
    )

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "scaler": scaler,
        "feature_columns": FEATURE_COLUMNS,
    }


def save_scaler(scaler, ticker: str) -> None:
    """Persist the fitted scaler so predict.py can inverse-transform forecasts later."""
    scaler_path = config.scalers_dir / f"{ticker}_scaler.joblib"
    joblib.dump(scaler, scaler_path)
    logger.info(f"Saved scaler for {ticker} to {scaler_path}")


if __name__ == "__main__":
    for ticker in config.tickers:
        build_dataset(ticker)