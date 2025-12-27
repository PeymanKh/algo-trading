"""
Thread-Safe in-memory storage

This module implements thread-safe Memory class to store and retrieve trades.
It uses threading.Lock to guarantee race conditions will not happen. Also, it uses
collections.deque to avoid infinity grow of trades in memory. At the end, this module
provides a thread-safe singleton factory for Memory instance which can be used by other modules.

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import logging
import threading
from collections import deque
from datetime import datetime, timedelta

from src.utils.schema import Trade


# Singleton instance and lock
_memory_instance = None
_memory_lock = threading.Lock()

# Logger
logger = logging.getLogger(__name__)


class Memory:
    def __init__(self, max_trades_per_symbol: int = 1000) -> None:
        """
        Memory constructor. It initializes a dictionary to store trades per symbol, a lock to synchronize access,
        and a maximum number of trades per symbol.

        Args:
            max_trades_per_symbol (int, optional): Maximum number of trades to store per symbol. Defaults to 1000.

        Raises:
            ValueError: If max_trades_per_symbol is not a positive integer.
        """
        # Validation
        if not isinstance(max_trades_per_symbol, int) or max_trades_per_symbol <= 0:
            raise ValueError("max_trades_per_symbol must be a positive integer")

        self.__trades = {}
        self.__lock = threading.Lock()
        self.__max_trades_per_symbol = max_trades_per_symbol

    def add_trade(self, trade: Trade) -> None:
        """
        Adds a new trade to the memory. This function uses lock to avoid race conditions.

        Args:
            trade (Trade): Trade to add.

        Raises:
            ValueError: If trade is not of type Trade.
        """
        # Validation
        if not isinstance(trade, Trade):
            raise ValueError("Trade must be of type Trade")

        # Thread-safe logic
        with self.__lock:
            if trade.symbol not in self.__trades:
                self.__trades[trade.symbol] = deque(maxlen=self.__max_trades_per_symbol)

            self.__trades[trade.symbol].append(trade)

    def get_last_n_trades(self, symbol: str, n: int = 10) -> list[Trade]:
        """
        Returns the last n trades for a given symbol. If the symbol is not found, returns an empty list.

        Args:
            symbol (str): Symbol to get trades for.
            n (int, optional): Number of trades to return. Defaults to 10.

        Raises:
            ValueError: If symbol or n are not valid.
            ValueError: If n is not a positive integer.
        """
        # Validations
        if not isinstance(symbol, str):
            raise ValueError("symbol must be a string")
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer")

        # Thread-safe logic
        with self.__lock:
            if symbol not in self.__trades:
                return []

            return list(self.__trades[symbol])[-n:]

    def get_trades_last_n_second(self, symbol: str, seconds: int = 10) -> list[Trade]:
        """
        Returns the last n trades for a given symbol that were executed within the last n seconds.
        To reduce lock time, this function copies the trades under the lock and filters them outside the lock.

        Args:
            symbol (str): Symbol to get trades for.
            seconds (int, optional): Number of seconds to consider. Defaults to 10.

        Raises:
            ValueError: If symbol or n are not valid.
            ValueError: If seconds is not a positive integer.
        """
        # Validation
        if not isinstance(symbol, str):
            raise ValueError("symbol must be a string")
        if not isinstance(seconds, int) or seconds <= 0:
            raise ValueError("seconds must be a positive integer")

        # Copy the trades under the lock
        with self.__lock:

            if symbol not in self.__trades:
                return []
            trades = list(self.__trades[symbol])

        # Filter outside lock to reduce lock time
        cutoff = datetime.now() - timedelta(seconds=seconds)
        cutoff_ms = int(cutoff.timestamp() * 1000)

        return [t for t in trades if t.trade_time >= cutoff_ms]

    def get_all_symbols(self) -> list[str]:
        """Returns list of all symbols with trades."""
        # Thread-safe logic
        with self.__lock:
            return list(self.__trades.keys())


def get_memory() -> Memory:
    """Thread-safe singleton factory for Memory instance."""
    global _memory_instance
    if _memory_instance is None:
        logger.debug("Creating a new Memory instance...")
        with _memory_lock:
            if _memory_instance is None:
                _memory_instance = Memory()
    return _memory_instance
