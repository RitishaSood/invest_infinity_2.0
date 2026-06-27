"""
models/predict.py
──────────────────
Loads trained models and generates two kinds of forecasts:

1. **In-sample test predictions** — model outputs on the held-out test
   sequences, used by the evaluation layer to compute RMSE / MAE / MAPE.

2. **Future price forecast** — iterative multi-step prediction for
   ``CFG.forecast_horizon`` trading days beyond the last known date.

Why this file exists
────────────────────
Prediction logic requires careful inverse-scaling (back to real dollar
values) and different data preparation for test-set evaluation vs. future
forecasting.  Keeping it separate from the model definitions and training
code lets ``evaluation/`` and the FastAPI routes call it cleanly without
reimplementing the scaling roundtrip.

All public functions return plain Python dicts / lists so the FastAPI layer
can serialise them to JSON with ``json.dumps`` directly.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras

from config.config import CFG
from data.dataset_builder import TickerDataset
from models.model_loader import load_model_and_scaler

logger = logging.getLogger(__name__)


# ── In-sample test predictions ────────────────────────────────────────────────


def predict_test_set(
    model: keras.Model,
    dataset: TickerDataset,
    scaler: Optional[MinMaxScaler] = None,
    target_col_index: int = 0,
) -> Dict[str, list]:
    """
    Run the model over ``dataset.X_test`` and inverse-transform the outputs
    back to real price values.

    Parameters
    ----------
    model : keras.Model
        A trained LSTM or GRU model.
    dataset : TickerDataset
        The dataset for one ticker; provides ``X_test``, ``y_test``,
        and the fitted scaler.
    scaler : MinMaxScaler, optional
        Overrides ``dataset.scaler`` when provided.
    target_col_index : int
        Column index of the target variable inside the scaler's feature
        space.  Defaults to ``0`` (``Close`` is always first).

    Returns
    -------
    dict with keys:
        ``"dates"``         — ISO-8601 date strings (test period)
        ``"actual"``        — real Close prices (float list)
        ``"predicted"``     — model-predicted Close prices (float list)
        ``"ticker"``        — stock symbol string
    """
    scaler = scaler or dataset.scaler
    n_features = dataset.n_features

    # Raw scaled predictions — shape (n_samples, 1)
    y_pred_scaled: np.ndarray = model.predict(dataset.X_test, verbose=0)

    # Inverse-transform requires a full (n_samples, n_features) matrix;
    # we fill dummy zeros for non-target columns.
    y_actual_inv = _inverse_transform_target(
        dataset.y_test.reshape(-1, 1), scaler, n_features, target_col_index
    )
    y_pred_inv = _inverse_transform_target(
        y_pred_scaled, scaler, n_features, target_col_index
    )

    # Align dates: test_df starts `sequence_length` rows into the test split
    test_dates = _extract_test_dates(dataset)

    return {
        "ticker": dataset.ticker,
        "dates": test_dates,
        "actual": y_actual_inv.tolist(),
        "predicted": y_pred_inv.tolist(),
    }


# ── Future forecast ───────────────────────────────────────────────────────────


def predict_future(
    model: keras.Model,
    dataset: TickerDataset,
    forecast_horizon: Optional[int] = None,
    scaler: Optional[MinMaxScaler] = None,
    target_col_index: int = 0,
) -> Dict[str, list]:
    """
    Generate an iterative multi-step price forecast beyond the last known date.

    The strategy is *recursive forecasting*: the model's last prediction is
    appended to the input window before generating the next step.  Non-target
    feature columns are held constant at their last observed values (a common
    simplifying assumption — the alternative requires forecasting every
    indicator independently).

    Parameters
    ----------
    model : keras.Model
        Trained LSTM or GRU model.
    dataset : TickerDataset
        Source dataset; the last ``sequence_length`` rows of the test split
        form the initial forecast seed.
    forecast_horizon : int, optional
        Number of future trading days to predict.
        Defaults to ``CFG.forecast_horizon``.
    scaler : MinMaxScaler, optional
        Overrides ``dataset.scaler`` when provided.
    target_col_index : int
        Index of ``Close`` in the feature matrix.  Defaults to ``0``.

    Returns
    -------
    dict with keys:
        ``"dates"``         — ISO-8601 strings for each forecast date
        ``"predicted"``     — forecasted Close prices (float list)
        ``"ticker"``        — stock symbol string
        ``"last_known_price"`` — last real Close price (float)
        ``"forecast_horizon"`` — number of days forecast (int)
    """
    forecast_horizon = forecast_horizon or CFG.forecast_horizon
    scaler = scaler or dataset.scaler
    seq_len = CFG.sequence_length
    n_features = dataset.n_features

    # Seed window: last `seq_len` rows of the scaled test data
    # We rebuild the scaled test array from the unscaled test_df
    test_scaled = scaler.transform(
        dataset.test_df[dataset.feature_columns].values
    )

    if len(test_scaled) < seq_len:
        raise ValueError(
            f"Test set too short ({len(test_scaled)} rows) for a "
            f"sequence_length of {seq_len}. Use more historical data."
        )

    # Rolling window — shape (seq_len, n_features)
    window: np.ndarray = test_scaled[-seq_len:].copy()

    future_scaled: List[float] = []

    for _ in range(forecast_horizon):
        # model expects (1, seq_len, n_features)
        x = window[np.newaxis, :, :]
        pred_scaled = float(model.predict(x, verbose=0)[0, 0])
        future_scaled.append(pred_scaled)

        # Build the next row: copy the last row, update the target column
        next_row = window[-1].copy()
        next_row[target_col_index] = pred_scaled

        # Slide window forward by one step
        window = np.vstack([window[1:], next_row])

    # Inverse-transform the forecast
    future_arr = np.array(future_scaled, dtype=np.float32).reshape(-1, 1)
    future_prices = _inverse_transform_target(
        future_arr, scaler, n_features, target_col_index
    )

    # Build trading-day date sequence starting from the day after the last date
    last_date = dataset.test_df.index[-1]
    if isinstance(last_date, str):
        last_date = pd.Timestamp(last_date)
    forecast_dates = _generate_trading_dates(last_date, forecast_horizon)

    last_known_price = float(dataset.test_df[CFG.target_column].iloc[-1])

    return {
        "ticker": dataset.ticker,
        "dates": forecast_dates,
        "predicted": future_prices.tolist(),
        "last_known_price": last_known_price,
        "forecast_horizon": forecast_horizon,
    }


# ── Convenience: load-then-predict ────────────────────────────────────────────


def generate_forecasts(
    ticker: str,
    model_type: str,
    dataset: TickerDataset,
    forecast_horizon: Optional[int] = None,
) -> Dict[str, dict]:
    """
    Load a trained model and return both test-set and future forecasts.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    model_type : str
        ``"lstm"`` or ``"gru"``.
    dataset : TickerDataset
        Pre-built dataset for *ticker*.
    forecast_horizon : int, optional
        Future forecast horizon in trading days.

    Returns
    -------
    dict with keys ``"test"`` and ``"future"``, each being the dict
    returned by :func:`predict_test_set` / :func:`predict_future`.
    """
    model, scaler = load_model_and_scaler(ticker, model_type)

    test_result = predict_test_set(model, dataset, scaler)
    future_result = predict_future(model, dataset, forecast_horizon, scaler)

    logger.info(
        "Forecasts generated for %s [%s] — %d test points, %d future days",
        ticker,
        model_type.upper(),
        len(test_result["predicted"]),
        future_result["forecast_horizon"],
    )

    return {"test": test_result, "future": future_result}


# ── Private helpers ───────────────────────────────────────────────────────────


def _inverse_transform_target(
    scaled_col: np.ndarray,
    scaler: MinMaxScaler,
    n_features: int,
    target_col_index: int,
) -> np.ndarray:
    """
    Inverse-scale a single target column back to its original price range.

    MinMaxScaler's ``inverse_transform`` requires the full feature matrix.
    We build a dummy zero matrix of shape ``(n_samples, n_features)``,
    place the scaled target values in the correct column, then extract
    only that column after transforming.
    """
    n_samples = scaled_col.shape[0]
    dummy = np.zeros((n_samples, n_features), dtype=np.float32)
    dummy[:, target_col_index] = scaled_col[:, 0]
    inverted = scaler.inverse_transform(dummy)
    return inverted[:, target_col_index]


def _extract_test_dates(dataset: TickerDataset) -> List[str]:
    """
    Return ISO-8601 date strings aligned to the test-set sequence outputs.

    The first ``sequence_length`` rows of test_df are consumed as the seed
    window, so the first output date is at index ``sequence_length``.
    """
    seq_len = CFG.sequence_length
    dates = dataset.test_df.index[seq_len:]
    return [str(d.date()) if hasattr(d, "date") else str(d) for d in dates]


def _generate_trading_dates(
    start: pd.Timestamp,
    n_days: int,
) -> List[str]:
    """
    Generate a list of *n_days* approximate trading dates after *start*.

    Uses ``pandas.bdate_range`` (business-day range) to skip weekends.
    Public holidays are not excluded (would require a calendar library)
    but this is sufficient for a forecasting prototype.
    """
    dates = pd.bdate_range(start=start + pd.Timedelta(days=1), periods=n_days)
    return [str(d.date()) for d in dates]