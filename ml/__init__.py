"""
Invest Infinity - Machine Learning Package

This package contains the full ML pipeline for the Invest Infinity platform:
data collection, preprocessing, feature engineering, LSTM/GRU forecasting
models, evaluation, and end-to-end pipelines.

Sub-packages:
    config      -> Centralized configuration (settings.yaml + config.py)
    data        -> Data fetching, cleaning, feature engineering, dataset building
    models      -> LSTM/GRU model definitions, training, prediction
    evaluation  -> Metrics, model comparison, backtesting, visualization
    pipelines   -> High-level orchestration scripts (training & forecasting)
"""

__version__ = "1.0.0"