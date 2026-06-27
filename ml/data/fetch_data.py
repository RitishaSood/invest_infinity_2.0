"""
data/fetch_data.py
──────────────────
Downloads historical OHLCV price data from Yahoo Finance via ``yfinance``
for one or more stock tickers and persists each ticker as a CSV file.

Why this file exists
────────────────────
All downstream steps (preprocessing, feature engineering, model training)
need a reliable, versioned snapshot of raw market data on disk.  Separating
the fetch step means the network is only hit once; every other module reads
from ``data/raw/<TICKER>.csv`` instead of calling the API every run.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf

from config.config import CFG

logger = logging.getLogger(__name__)


# ── Public API ──────────────────────────────────────────────────────────────


def fetch_ticker(
    ticker: str,
    start_date: str,
    end_date: str,
    save_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Download daily OHLCV data for a single ticker and optionally save to CSV.

    Parameters
    ----------
    ticker : str
        Stock symbol (e.g. ``"AAPL"``).
    start_date : str
        ISO-8601 start date (``"YYYY-MM-DD"``).
    end_date : str
        ISO-8601 end date or ``"today"``.
    save_dir : Path, optional
        Directory where ``<TICKER>.csv`` will be written.  If ``None`` the
        file is not saved.

    Returns
    -------
    pd.DataFrame
        Raw OHLCV DataFrame indexed by ``Date``.

    Raises
    ------
    ValueError
        If yfinance returns an empty DataFrame (invalid ticker or date range).
    """
    resolved_end = str(date.today()) if end_date == "today" else end_date
    logger.info("Fetching %s  [%s → %s]", ticker, start_date, resolved_end)

    df: pd.DataFrame = yf.download(
        ticker,
        start=start_date,
        end=resolved_end,
        progress=False,
        auto_adjust=True,   # adjusts for splits/dividends automatically
    )

    if df.empty:
        raise ValueError(
            f"No data returned for ticker '{ticker}'. "
            "Check the symbol and date range."
        )

    # Flatten multi-level columns that yfinance sometimes returns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index.name = "Date"
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.sort_index(inplace=True)

    logger.info("  → %d rows downloaded for %s", len(df), ticker)

    if save_dir is not None:
        _save_csv(df, ticker, Path(save_dir))

    return df


def fetch_multiple_tickers(
    tickers: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    save_dir: Optional[Path] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Download data for a list of tickers, returning a dict of DataFrames.

    Falls back to ``CFG`` values for any argument left as ``None``.

    Parameters
    ----------
    tickers : list[str], optional
        Symbols to download.  Defaults to ``CFG.tickers``.
    start_date : str, optional
        Start date.  Defaults to ``CFG.start_date``.
    end_date : str, optional
        End date.  Defaults to ``CFG.end_date``.
    save_dir : Path, optional
        Directory for CSV output.  Defaults to ``CFG.raw_data_dir``.

    Returns
    -------
    dict[str, pd.DataFrame]
        Mapping of ``ticker → DataFrame``.  Tickers that fail are logged
        and skipped rather than crashing the whole run.
    """
    tickers = tickers or CFG.tickers
    start_date = start_date or CFG.start_date
    end_date = end_date or CFG.end_date
    save_dir = Path(save_dir) if save_dir else CFG.raw_data_dir

    results: Dict[str, pd.DataFrame] = {}

    for ticker in tickers:
        try:
            df = fetch_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                save_dir=save_dir,
            )
            results[ticker] = df
        except Exception as exc:
            logger.warning("Skipping %s — %s", ticker, exc)

    logger.info(
        "Fetch complete: %d / %d tickers succeeded.",
        len(results),
        len(tickers),
    )
    return results


def load_ticker_from_csv(
    ticker: str,
    data_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Load a previously saved raw CSV for ``ticker``.

    Parameters
    ----------
    ticker : str
        Stock symbol.
    data_dir : Path, optional
        Directory containing ``<TICKER>.csv``.  Defaults to ``CFG.raw_data_dir``.

    Returns
    -------
    pd.DataFrame
        OHLCV DataFrame with a ``datetime`` index named ``"Date"``.

    Raises
    ------
    FileNotFoundError
        If the CSV has not yet been downloaded.
    """
    data_dir = Path(data_dir) if data_dir else CFG.raw_data_dir
    path = data_dir / f"{ticker}.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"No raw data found for '{ticker}' at {path}. "
            "Run fetch_multiple_tickers() first."
        )

    df = pd.read_csv(path, index_col="Date", parse_dates=True)
    logger.info("Loaded %s from %s (%d rows)", ticker, path, len(df))
    return df


# ── Helpers ─────────────────────────────────────────────────────────────────


def _save_csv(df: pd.DataFrame, ticker: str, save_dir: Path) -> None:
    """Write *df* to ``<save_dir>/<ticker>.csv``."""
    save_dir.mkdir(parents=True, exist_ok=True)
    path = save_dir / f"{ticker}.csv"
    df.to_csv(path)
    logger.info("  → Saved to %s", path)


# ── CLI entry-point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    data = fetch_multiple_tickers()
    for sym, frame in data.items():
        print(f"{sym}: {len(frame)} rows  |  {frame.index[0].date()} → {frame.index[-1].date()}")