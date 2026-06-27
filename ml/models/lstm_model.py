"""
models/lstm_model.py
─────────────────────
Defines and builds the multi-layer LSTM (Long Short-Term Memory) model
used for stock price forecasting.

Why this file exists
────────────────────
Isolating the architecture in its own module means the training script,
evaluation harness, and forecasting pipeline can all import a single
``build_lstm_model()`` factory function without knowing about Keras
internals.  Swapping a layer or changing the regularisation strategy
only ever touches this one file.

Architecture
────────────
  Input → LSTM(units[0], return_sequences=True) → Dropout
        → LSTM(units[1], return_sequences=False) → Dropout
        → Dense(25, relu)
        → Dense(1)           ← single next-step price prediction

The number of LSTM layers is driven by ``CFG.lstm_units``; adding a
third layer is as simple as appending another value to that list.
"""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers  # type: ignore[attr-defined]

from config.config import CFG

logger = logging.getLogger(__name__)


# ── Model factory ────────────────────────────────────────────────────────────


def build_lstm_model(
    input_shape: Tuple[int, int],
    lstm_units: Optional[List[int]] = None,
    dropout_rate: Optional[float] = None,
    learning_rate: Optional[float] = None,
    l2_reg: float = 1e-4,
) -> keras.Model:
    """
    Construct, compile, and return a stacked LSTM model.

    Parameters
    ----------
    input_shape : tuple[int, int]
        ``(sequence_length, n_features)`` — shape of a single input sample
        (batch dimension excluded).
    lstm_units : list[int], optional
        Number of hidden units for each LSTM layer.  The length of the list
        determines the number of stacked layers.  Defaults to ``CFG.lstm_units``.
    dropout_rate : float, optional
        Dropout probability applied after each LSTM layer.
        Defaults to ``CFG.dropout_rate``.
    learning_rate : float, optional
        Adam learning rate.  Defaults to ``CFG.learning_rate``.
    l2_reg : float
        L2 kernel regularisation strength applied to each LSTM layer.
        Defaults to ``1e-4``.

    Returns
    -------
    keras.Model
        Compiled model ready for ``.fit()``.

    Notes
    -----
    * All LSTM layers except the last use ``return_sequences=True`` so that
      each layer receives the full hidden-state sequence from the layer below.
    * The final Dense(1) output is a raw real-valued regression target
      (scaled close price).  No activation is applied.
    """
    lstm_units = lstm_units or CFG.lstm_units
    dropout_rate = dropout_rate if dropout_rate is not None else CFG.dropout_rate
    learning_rate = learning_rate or CFG.learning_rate

    if len(lstm_units) < 1:
        raise ValueError("lstm_units must contain at least one element.")

    model = keras.Sequential(name="LSTM_Forecaster")
    model.add(keras.Input(shape=input_shape, name="input"))

    for i, units in enumerate(lstm_units):
        is_last_lstm = i == len(lstm_units) - 1
        model.add(
            layers.LSTM(
                units=units,
                return_sequences=not is_last_lstm,
                kernel_regularizer=regularizers.l2(l2_reg),
                recurrent_regularizer=regularizers.l2(l2_reg),
                name=f"lstm_{i + 1}",
            )
        )
        model.add(layers.Dropout(rate=dropout_rate, name=f"dropout_{i + 1}"))

    # Intermediate dense layer adds capacity without extra recurrent cost
    model.add(layers.Dense(25, activation="relu", name="dense_intermediate"))
    model.add(layers.Dense(1, name="output"))

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mean_squared_error",
        metrics=["mae"],
    )

    logger.info(
        "LSTM model built — input=%s  layers=%s  dropout=%.2f  lr=%.4f",
        input_shape,
        lstm_units,
        dropout_rate,
        learning_rate,
    )
    model.summary(print_fn=logger.debug)
    return model


# ── Callbacks ────────────────────────────────────────────────────────────────


def get_lstm_callbacks(
    model_save_path: str,
    patience: Optional[int] = None,
    monitor: str = "val_loss",
) -> List[keras.callbacks.Callback]:
    """
    Return the standard callback stack used when training the LSTM.

    Callbacks
    ---------
    * **ModelCheckpoint** — saves the best weights (by ``monitor``) to
      ``model_save_path`` during training so the optimal state is not lost
      if training continues past the best epoch.
    * **EarlyStopping** — halts training once ``monitor`` stops improving
      for ``patience`` consecutive epochs and restores the best weights.
    * **ReduceLROnPlateau** — halves the learning rate after 5 non-improving
      epochs (min lr = 1e-6) to escape shallow local minima.

    Parameters
    ----------
    model_save_path : str
        Full path (including filename) where the best model is saved,
        e.g. ``"saved_models/lstm/AAPL_lstm.keras"``.
    patience : int, optional
        Early-stopping patience.  Defaults to ``CFG.patience``.
    monitor : str
        Metric to monitor.  Defaults to ``"val_loss"``.

    Returns
    -------
    list[keras.callbacks.Callback]
    """
    patience = patience or CFG.patience

    checkpoint = keras.callbacks.ModelCheckpoint(
        filepath=model_save_path,
        monitor=monitor,
        save_best_only=True,
        save_weights_only=False,
        verbose=0,
    )

    early_stop = keras.callbacks.EarlyStopping(
        monitor=monitor,
        patience=patience,
        restore_best_weights=True,
        verbose=1,
    )

    reduce_lr = keras.callbacks.ReduceLROnPlateau(
        monitor=monitor,
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1,
    )

    return [checkpoint, early_stop, reduce_lr]