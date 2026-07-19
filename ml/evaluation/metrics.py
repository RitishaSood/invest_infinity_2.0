"""
evaluation/metrics.py

Standard regression metrics for evaluating forecast accuracy. This file
has no project-specific imports - it just takes two arrays of numbers
(actual vs predicted) and scores them, so it's easy to test in isolation.
"""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error - penalizes large errors more than small ones."""
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error - average absolute difference between predictions and actuals."""
    return float(mean_absolute_error(y_true, y_pred))


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error - average error as a percentage of the actual value."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)


def calculate_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """R2 score - how much better the model is than always predicting the mean (1.0 = perfect)."""
    return float(r2_score(y_true, y_pred))


def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute RMSE, MAE, MAPE, and R2 at once and return them as a dictionary."""
    return {
        "rmse": round(calculate_rmse(y_true, y_pred), 4),
        "mae": round(calculate_mae(y_true, y_pred), 4),
        "mape": round(calculate_mape(y_true, y_pred), 4),
        "r2": round(calculate_r2(y_true, y_pred), 4),
    }   