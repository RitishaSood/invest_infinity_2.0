"""
evaluation/backtesting.py

Evaluates how a trained model performs on historical data it has NOT
seen during training (the test set), by running it on the whole test
set at once and comparing predictions to actual prices.
"""

from typing import Dict, Literal

from data.dataset_builder import CLOSE_COLUMN_INDEX, FEATURE_COLUMNS, build_dataset
from data.preprocess import inverse_transform_column
from evaluation.metrics import calculate_all_metrics
from models.model_loader import load_model, load_scaler
from utils.logger import get_logger

logger = get_logger(__name__)

ModelType = Literal["lstm", "gru"]


def run_backtest(ticker: str, model_type: ModelType) -> Dict[str, object]:
    """
    Backtest a trained model on its held-out test set.

    Returns a dict with day-by-day actual prices, predicted prices, and
    summary metrics - ready to hand to visualization.py or the frontend
    dashboard.
    """
    dataset = build_dataset(ticker)
    model = load_model(ticker, model_type)
    scaler = load_scaler(ticker)

    scaled_predictions = model.predict(dataset["X_test"], verbose=0).flatten()
    scaled_actuals = dataset["y_test"]

    predicted_prices = inverse_transform_column(
        scaler, scaled_predictions, CLOSE_COLUMN_INDEX, len(FEATURE_COLUMNS)
    )
    actual_prices = inverse_transform_column(
        scaler, scaled_actuals, CLOSE_COLUMN_INDEX, len(FEATURE_COLUMNS)
    )

    metrics = calculate_all_metrics(actual_prices, predicted_prices)
    logger.info(f"Backtest for {ticker} ({model_type.upper()}): {metrics}")

    return {
        "ticker": ticker,
        "model_type": model_type,
        "actual_prices": actual_prices.round(2).tolist(),
        "predicted_prices": predicted_prices.round(2).tolist(),
        "metrics": metrics,
    }


if __name__ == "__main__":
    from config.config import config

    for ticker in config.tickers:
        run_backtest(ticker, "lstm")