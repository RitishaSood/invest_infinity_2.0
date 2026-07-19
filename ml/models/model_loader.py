"""
models/model_loader.py

Loads saved LSTM/GRU models and their matching scalers from disk. Used by
predict.py and the forecasting pipeline, which should never care about
file paths directly - just ask this module for a model by ticker name.
"""

from pathlib import Path
from typing import Literal

import joblib
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

from config.config import config
from utils.logger import get_logger

logger = get_logger(__name__)

ModelType = Literal["lstm", "gru"]


def _get_model_path(ticker: str, model_type: ModelType) -> Path:
    """Return the expected saved-model file path for a ticker and model type."""
    model_dir = config.lstm_model_dir if model_type == "lstm" else config.gru_model_dir
    return model_dir / f"{ticker}_{model_type}.keras"


def load_model(ticker: str, model_type: ModelType) -> tf.keras.Model:
    """
    Load a trained LSTM or GRU model for a given ticker.

    Raises a clear FileNotFoundError (instead of a confusing TensorFlow
    error) if the model hasn't been trained yet.
    """
    model_path = _get_model_path(ticker, model_type)

    if not model_path.exists():
        raise FileNotFoundError(
            f"No trained {model_type.upper()} model found for '{ticker}' "
            f"at {model_path}. Run training_pipeline.py first."
        )

    logger.info(f"Loading {model_type.upper()} model for {ticker} from {model_path}")
    return tf.keras.models.load_model(model_path)


def load_scaler(ticker: str) -> MinMaxScaler:
    """
    Load the fitted MinMaxScaler saved for a given ticker.

    Raises a clear FileNotFoundError if the dataset hasn't been built yet.
    """
    scaler_path = config.scalers_dir / f"{ticker}_scaler.joblib"

    if not scaler_path.exists():
        raise FileNotFoundError(
            f"No scaler found for '{ticker}' at {scaler_path}. "
            f"Run dataset_builder.build_dataset() first."
        )

    logger.info(f"Loading scaler for {ticker} from {scaler_path}")
    return joblib.load(scaler_path)