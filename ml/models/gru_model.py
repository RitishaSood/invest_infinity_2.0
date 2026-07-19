"""
models/gru_model.py

Defines a small, configurable multi-layer GRU model for stock price
forecasting. Mirrors lstm_model.py's structure - the only difference is
the recurrent layer type - so the two are easy to compare side by side.
"""

from typing import Tuple

import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l1_l2

from config.config import config


def build_gru_model(input_shape: Tuple[int, int]) -> tf.keras.Model:
    """
    Build and compile a multi-layer GRU model.

    input_shape: (sequence_length, num_features), e.g. (60, 8)
    Output: a single scaled value - the predicted next closing price.
    """
    model = Sequential(name="GRU_Forecaster")
    regularizer = l1_l2(l1=config.l1_reg, l2=config.l2_reg)

    # First GRU layer needs input_shape. return_sequences=True is required
    # whenever another recurrent layer follows it.
    model.add(GRU(
        units=config.gru_units[0],
        return_sequences=len(config.gru_units) > 1,
        input_shape=input_shape,
        kernel_regularizer=regularizer,
    ))
    model.add(Dropout(config.dropout_rate))

    # Any additional stacked GRU layers (e.g. gru_units = [64, 32] adds one more).
    remaining_units = config.gru_units[1:]
    for i, units in enumerate(remaining_units):
        is_last_recurrent_layer = i == len(remaining_units) - 1
        model.add(GRU(
            units=units,
            return_sequences=not is_last_recurrent_layer,
            kernel_regularizer=regularizer,
        ))
        model.add(Dropout(config.dropout_rate))

    model.add(Dense(1))  # Single predicted value (scaled closing price)

    model.compile(
        optimizer=Adam(learning_rate=config.learning_rate),
        loss="mse",
        metrics=["mae"],
    )
    return model


def get_early_stopping_callback(patience: int = 5) -> EarlyStopping:
    """Stop training when validation loss stops improving, and restore the best weights."""
    return EarlyStopping(
        monitor="val_loss",
        patience=patience,
        restore_best_weights=True,
    )