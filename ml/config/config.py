"""
config/config.py

Centralized configuration loader for the Invest Infinity ML pipeline.

Every other file in this project should import settings from here instead
of hardcoding values or paths. This keeps the whole pipeline consistent -
change a value once in settings.yaml, and it applies everywhere.

Usage:
    from config.config import config

    print(config.sequence_length)
    print(config.raw_data_dir)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import yaml

# Root of the ml/ package (one level up from this config/ folder).
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "config" / "settings.yaml"


def _load_yaml(path: Path) -> dict:
    """Read a YAML file and return its contents as a plain dictionary."""
    with open(path, "r") as file:
        return yaml.safe_load(file)


@dataclass
class Config:
    """
    Holds every configurable value used across the ML pipeline.

    Fields are split into two groups:
      1. Values loaded directly from settings.yaml.
      2. Folder paths, which are computed automatically in __post_init__.
    """

    # ---- Loaded from settings.yaml ----
    sequence_length: int
    forecast_horizon: int
    batch_size: int
    epochs: int
    random_seed: int
    learning_rate: float

    tickers: List[str]
    start_date: str
    end_date: str
    train_test_split: float

    # ---- Computed automatically (not set from YAML) ----
    raw_data_dir: Path = field(init=False)
    saved_models_dir: Path = field(init=False)
    lstm_model_dir: Path = field(init=False)
    gru_model_dir: Path = field(init=False)
    scalers_dir: Path = field(init=False)
    plots_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        """Resolve all folder paths and make sure they exist on disk."""
        self.raw_data_dir = BASE_DIR / "data" / "raw"
        self.saved_models_dir = BASE_DIR / "saved_models"
        self.lstm_model_dir = self.saved_models_dir / "lstm"
        self.gru_model_dir = self.saved_models_dir / "gru"
        self.scalers_dir = self.saved_models_dir / "scalers"
        self.plots_dir = BASE_DIR / "plots"

        self._create_required_folders()

    def _create_required_folders(self) -> None:
        """Create any missing output folders so later steps never fail."""
        required_folders = [
            self.raw_data_dir,
            self.lstm_model_dir,
            self.gru_model_dir,
            self.scalers_dir,
            self.plots_dir,
        ]
        for folder in required_folders:
            folder.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load settings.yaml from disk and return a ready-to-use Config object."""
    raw_settings = _load_yaml(SETTINGS_PATH)
    return Config(**raw_settings)


# Singleton config instance - import this everywhere else in the project.
config = load_config()