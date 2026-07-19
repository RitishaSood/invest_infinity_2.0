"""
models/predict.py

Loads a trained model and generates a future price forecast.

Forecasting approach: the model is trained to predict only the NEXT day's
closing price. To forecast further into the future (config.forecast_horizon
days), we feed each prediction back into the model to predict the day after
that (this is called autoregressive forecasting).

Simplification: while rolling the window forward, the technical indicator
columns (MA20, RSI, MACD, etc.) are held at their last known values instead
of being fully recalculated at every step. Recomputing rolling indicators
day-by-day inside the loop would add real complexity for little benefit in
a portfolio project, so only the "Close" column is updated with each new
prediction.
"""

from typing import List, Literal

import numpy as np

from config.config import config
from data.dataset_builder import CLOSE_COLUMN_INDEX, FEATURE_COLUMNS
from data.feature_engineering import generate_features
from data.fetch_data import load_raw_data
from data.preprocess import handle_missing_values, handle_outliers, inverse_transform_column
from models.model_loader import load_model, load_scaler
from utils.logger import get_logger

logger = get_logger(__name__)

ModelType = Literal["lstm", "gru"]


def _prepare_latest_window(ticker: str) -> np.ndarray:
    """Rebuild features for a ticker and return the most recent scaled sequence window."""
    raw_df = load_raw_data(ticker)
    clean_df = handle_missing_values(raw_df)
    clean_df = handle_outliers(clean_df)
    featured_df = generate_features(clean_df)

    scaler = load_scaler(ticker)
    scaled_values = scaler.transform(featured_df[FEATURE_COLUMNS])

    latest_window = scaled_values[-config.sequence_length :]
    return latest_window


def _inverse_transform_close_prices(scaled_closes: List[float], ticker: str) -> List[float]:
    """Convert scaled predicted closing prices back into real dollar values."""
    scaler = load_scaler(ticker)
    real_values = inverse_transform_column(
        scaler, np.array(scaled_closes), CLOSE_COLUMN_INDEX, len(FEATURE_COLUMNS)
    )
    return real_values.round(2).tolist()


def forecast_future_prices(ticker: str, model_type: ModelType, steps: int = None) -> List[float]:
    """
    Forecast future closing prices for a ticker using a trained model.

    steps defaults to config.forecast_horizon (e.g. 30 days).
    Returns a JSON-serializable list of predicted closing prices.
    """
    steps = steps or config.forecast_horizon
    model = load_model(ticker, model_type)
    current_window = _prepare_latest_window(ticker)  # shape: (sequence_length, num_features)

    scaled_predictions: List[float] = []

    for _ in range(steps):
        model_input = current_window.reshape(1, config.sequence_length, len(FEATURE_COLUMNS))
        predicted_close = float(model.predict(model_input, verbose=0)[0, 0])
        scaled_predictions.append(predicted_close)

        # Slide the window forward: drop the oldest day, append a new row
        # where Close is the new prediction and other features repeat the
        # last known values (see module docstring for why).
        next_row = current_window[-1].copy()
        next_row[CLOSE_COLUMN_INDEX] = predicted_close
        current_window = np.vstack([current_window[1:], next_row])

    logger.info(f"Generated {steps}-day forecast for {ticker} using {model_type.upper()}")
    return _inverse_transform_close_prices(scaled_predictions, ticker)


if __name__ == "__main__":
    for ticker in config.tickers:
        forecast = forecast_future_prices(ticker, "lstm")
        print(f"{ticker}: {forecast[:5]} ...")