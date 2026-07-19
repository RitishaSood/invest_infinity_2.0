"""
pipelines/forecasting_pipeline.py

Runs the full forecasting pipeline for a trained model:

    Load Model -> Load Scaler -> Predict Future Prices -> Plot Forecast

Assumes training_pipeline.py has already been run for the ticker, so a
trained model and scaler already exist on disk (model_loader.py will
raise a clear error if they don't).
"""

from typing import Dict, List, Literal

from config.config import config
from evaluation.visualization import plot_forecast
from models.predict import forecast_future_prices
from utils.logger import get_logger

logger = get_logger(__name__)

ModelType = Literal["lstm", "gru"]


def run_forecasting_pipeline(
    ticker: str, model_type: ModelType = "lstm", steps: int = None
) -> Dict[str, object]:
    """
    Generate and plot a future price forecast for a single ticker.

    steps defaults to config.forecast_horizon (e.g. 30 days).
    Returns a JSON-serializable dict: {"ticker", "model_type", "forecast"}.
    """
    steps = steps or config.forecast_horizon
    logger.info(f"Forecasting {steps} days ahead for {ticker} using {model_type.upper()}")

    forecast = forecast_future_prices(ticker, model_type, steps)
    plot_forecast(ticker, model_type, forecast)

    return {
        "ticker": ticker,
        "model_type": model_type,
        "forecast": forecast,
    }


def run_forecasting_pipeline_for_all(
    tickers: List[str] = None, model_type: ModelType = "lstm"
) -> Dict[str, dict]:
    """Run the forecasting pipeline for multiple tickers at once."""
    tickers = tickers or config.tickers
    results: Dict[str, dict] = {}

    for ticker in tickers:
        results[ticker] = run_forecasting_pipeline(ticker, model_type)

    return results


if __name__ == "__main__":
    run_forecasting_pipeline_for_all()