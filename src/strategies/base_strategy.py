"""
Base Strategy Class

This module defines an abstract base class for trading strategies.
Strategies generate signals, log them on terminal and to CSV file.

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import os
import csv
import logging
from pathlib import Path
from typing import Literal
from abc import ABC, abstractmethod


from src.utils.schema import WindowAnalytics


# Logger
logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.

    Responsibilities:
        1. Generate trading signals (BUY, SELL, HOLD)
        2. Log signals to the terminal and CSV file.
        3. Track basic statistics
    """

    def __init__(self, symbol: str, data_dir: str = "signals") -> None:
        """
        Strategy constructor.

        Args:
            symbol (str): Trading symbol to analyze
            data_dir (str, optional): Directory to store strategy data. Defaults to "signals".
        """
        self.__symbol = symbol
        self.__signal_count = {"BUY": 0, "SELL": 0, "HOLD": 0}

        # Create data directory if not exists
        Path(data_dir).mkdir(exist_ok=True)

        # Setup CSV file
        self.__csv_file_path = f"{data_dir}/{symbol}_signals.csv"
        self._init_csv()

    def _init_csv(self) -> None:
        """Initialize CSV file with headers."""
        if not os.path.exists(self.__csv_file_path):
            with open(self.__csv_file_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["timestamp", "symbol", "signal", "price", "reason"])

    @abstractmethod
    def generate_signal(
        self, analytics: WindowAnalytics
    ) -> tuple[Literal["BUT", "SEL", "HOLD"], str]:
        """
        Generate trading signal based on the given WindowAnalytics object.

        Args:
            analytics (WindowAnalytics): Market data for the current window.

        Returns:
            (Literal["BUT", "SEL", "HOLD"], str): Tuple containing the signal type and the reason.
        """
        pass

    def update(self, analytics: WindowAnalytics) -> None:
        """
        Update strategy with new data and log signal.

        Args:
            analytics: Latest market analytics
        """
        signal, reason = self.generate_signal(analytics)

        # Update counter
        self.__signal_count[signal] += 1

        # Log to CSV
        self._log_signal(analytics.last_trade_time, signal, analytics.ohlc.c, reason)

    def _log_signal(
        self, timestamp: int, signal: str, price: float, reason: str
    ) -> None:
        """Write signal to CSV file and log to terminal."""
        with open(self.__csv_file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, self.__symbol, signal, price, reason])

        logger.info(f"New Signal: {timestamp}, {signal}, {price}, {reason}")

    def get_stats(self) -> dict:
        """Return basic statistics."""
        total = sum(self.__signal_count.values())
        return {
            "symbol": self.__symbol,
            "total_signals": total,
            "buy_signals": self.__signal_count["BUY"],
            "sell_signals": self.__signal_count["SELL"],
            "hold_signals": self.__signal_count["HOLD"],
        }


# Expose BaseStrategy class to other modules
__all__ = ["BaseStrategy"]
