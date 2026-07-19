"""
data/fetch_data.py

Downloads historical stock price data using yfinance and saves it as CSV
files inside config.raw_data_dir. Later steps (preprocess, feature
engineering) read from these cached CSVs instead of re-downloading.
"""

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf

from config.config import config
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Download historical OHLCV data for a single ticker from Yahoo Finance."""
    logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df.empty:
        raise ValueError(
            f"No data returned for ticker '{ticker}'. Check the symbol or date range."
        )

    df = df.reset_index()  # Turn the Date index into a normal column
    return df


def save_raw_data(df: pd.DataFrame, ticker: str) -> Path:
    """Save a ticker's DataFrame to data/raw/<ticker>.csv."""
    file_path = config.raw_data_dir / f"{ticker}.csv"
    df.to_csv(file_path, index=False)
    logger.info(f"Saved raw data for {ticker} to {file_path}")
    return file_path


def load_raw_data(ticker: str) -> pd.DataFrame:
    """Load a previously saved raw CSV for a ticker."""
    file_path = config.raw_data_dir / f"{ticker}.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"No raw data found for '{ticker}'. Run fetch_and_save_all() first."
        )

    return pd.read_csv(file_path, parse_dates=["Date"])


def fetch_and_save_all(tickers: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
    """Fetch and save raw data for multiple tickers (defaults to config.tickers)."""
    tickers = tickers or config.tickers
    all_data: Dict[str, pd.DataFrame] = {}

    for ticker in tickers:
        df = fetch_stock_data(ticker, config.start_date, config.end_date)
        save_raw_data(df, ticker)
        all_data[ticker] = df

    return all_data


if __name__ == "__main__":
    fetch_and_save_all()