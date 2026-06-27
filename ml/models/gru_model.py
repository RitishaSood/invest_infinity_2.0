"""
models/gru_model.py
────────────────────
Defines and builds the multi-layer GRU (Gated Recurrent Unit) model
used for stock price forecasting.

Why this file exists
────────────────────
GRU is architecturally similar to LSTM but uses only two gates (reset and
update) instead of three, which reduces parameter count and often trains
faster on shorter sequences.  Keeping it in a separate module lets the
training script treat both architectures symmetrically — same interface,
different internals — and makes side-by-side comparison straightforward.

Architecture
────────────
  Input → GRU(units[0], return_sequences=True) → Dropout
        → GRU(units[1], return_sequences=False) → Dropout
        → Dense(25, relu)
        → Dense(1)           ← single next-step price prediction

Mirrors ``lstm_model.py`` exactly in structure so evaluation and training
code can call either model factory interchangeably.
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


def build_gru_model(
    input_shape: Tuple[int, int],
    gru_units: Optional[List[int]] = None,
    dropout_rate: Optional[float] = None,
    learning_rate: Optional[float] = None,
    l2_reg: float = 1e-4,
) -> keras.Model:
    """
    Construct, compile, and return a stacked GRU model.

    Parameters
    ----------
    input_shape : tuple[int, int]
        ``(sequence_length, n_features)`` — shape of a single input sample
        (batch dimension excluded).
    gru_units : list[int], optional
        Number of hidden units for each GRU layer.  List length determines
        the number of stacked layers.  Defaults to ``CFG.gru_units``.
    dropout_rate : float, optional
        Dropout probability applied after each GRU layer.
        Defaults to ``CFG.dropout_rate``.
    learning_rate : float, optional
        Adam learning rate.  Defaults to ``CFG.learning_rate``.
    l2_reg : float
        L2 kernel regularisation strength.  Defaults to ``1e-4``.

    Returns
    -------
    keras.Model
        Compiled model ready for ``.fit()``.

    Notes
    -----
    * All GRU layers except the last use ``return_sequences=True``.
    * GRU uses fewer parameters than LSTM (no separate cell state), so it
      can train faster and generalises better on smaller datasets.
    * ``reset_after=True`` (Keras default since TF 2.x) enables GPU-optimised
      cuDNN kernels when a compatible GPU is available.
    """
    gru_units = gru_units or CFG.gru_units
    dropout_rate = dropout_rate if dropout_rate is not None else CFG.dropout_rate
    learning_rate = learning_rate or CFG.learning_rate

    if len(gru_units) < 1:
        raise ValueError("gru_units must contain at least one element.")

    model = keras.Sequential(name="GRU_Forecaster")
    model.add(keras.Input(shape=input_shape, name="input"))

    for i, units in enumerate(gru_units):
        is_last_gru = i == len(gru_units) - 1
        model.add(
            layers.GRU(
                units=units,
                return_sequences=not is_last_gru,
                kernel_regularizer=regularizers.l2(l2_reg),
                recurrent_regularizer=regularizers.l2(l2_reg),
                reset_after=True,   # enables cuDNN acceleration on GPU
                name=f"gru_{i + 1}",
            )
        )
        model.add(layers.Dropout(rate=dropout_rate, name=f"dropout_{i + 1}"))

    model.add(layers.Dense(25, activation="relu", name="dense_intermediate"))
    model.add(layers.Dense(1, name="output"))

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mean_squared_error",
        metrics=["mae"],
    )

    logger.info(
        "GRU model built — input=%s  layers=%s  dropout=%.2f  lr=%.4f",
        input_shape,
        gru_units,
        dropout_rate,
        learning_rate,
    )
    model.summary(print_fn=logger.debug)
    return model


# ── Callbacks ────────────────────────────────────────────────────────────────


def get_gru_callbacks(
    model_save_path: str,
    patience: Optional[int] = None,
    monitor: str = "val_loss",
) -> List[keras.callbacks.Callback]:
    """
    Return the standard callback stack used when training the GRU.

    Identical contract to :func:`~models.lstm_model.get_lstm_callbacks` so
    the training script can call them interchangeably.

    Callbacks
    ---------
    * **ModelCheckpoint** — saves the best weights during training.
    * **EarlyStopping** — stops training once validation loss plateaus.
    * **ReduceLROnPlateau** — halves the learning rate after 5 stagnant
      epochs (floor = 1e-6).

    Parameters
    ----------
    model_save_path : str
        Full path for the best-model checkpoint file.
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