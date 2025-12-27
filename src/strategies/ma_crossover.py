"""
Moving Average Crossover Strategy

This strategy generates trading signals based on the crossover of two moving averages:
    - Short-term MA (fast): Recent price trend
    - Long-term MA (slow): Overall price trend

Signal Logic:
    - BUY: When short MA crosses above long MA (bullish signal)
    - SELL: When short MA crosses below long MA (bearish signal)
    - HOLD: When no crossover occurs

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import logging
from typing import Literal
from collections import deque

from src.strategies.base_strategy import BaseStrategy
from src.utils.schema import WindowAnalytics


# Logger
logger = logging.getLogger(__name__)


class MAStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.

    This strategy maintains a history of prices and calculates two moving averages.
    Trading signals are generated when these averages cross each other.
    """

    def __init__(
        self,
        symbol: str,
        short_window: int = 10,
        long_window: int = 30,
        data_dir: str = "signals",
    ) -> None:
        """
        Initialize MA Crossover Strategy.

        Args:
            symbol (str): Trading symbol to analyze
            short_window (int, optional): Short-term MA period. Defaults to 10.
            long_window (int, optional): Long-term MA period. Defaults to 30.
            data_dir (str, optional): Directory to store signals. Defaults to "signals".

        Raises:
            ValueError: If short_window >= long_window
        """
        # Validation
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")

        super().__init__(symbol, data_dir)

        self.__short_window = short_window
        self.__long_window = long_window

        # Store price history (using deque for efficient memory management)
        self.__prices = deque(maxlen=long_window)

        # Track previous MA values to detect crossovers
        self.__prev_short_ma = None
        self.__prev_long_ma = None

        logger.info(
            f"Initialized MAStrategy for {symbol}: "
            f"short={short_window}, long={long_window}"
        )

    def generate_signal(
        self, analytics: WindowAnalytics
    ) -> tuple[Literal["BUY", "SELL", "HOLD"], str]:
        """
        Generate trading signal based on MA crossover.

        Args:
            analytics (WindowAnalytics): Market data for the current window

        Returns:
            tuple: (signal, reason)
        """
        # Add latest closing price to history
        current_price = analytics.ohlc.c
        self.__prices.append(current_price)

        # Wait until we have enough data for long MA
        if len(self.__prices) < self.__long_window:
            return (
                "HOLD",
                f"Not enough data for long MA ({self.__long_window} required)",
            )

        # Calculate moving averages
        short_ma = self._calculate_ma(self.__short_window)
        long_ma = self._calculate_ma(self.__long_window)

        # First calculation - no crossover yet
        if self.__prev_short_ma is None or self.__prev_long_ma is None:
            self.__prev_short_ma = short_ma
            self.__prev_long_ma = long_ma
            return "HOLD", "First MA calculation"

        # Detect crossovers
        signal, reason = self._detect_crossover(short_ma, long_ma)

        # Update previous values
        self.__prev_short_ma = short_ma
        self.__prev_long_ma = long_ma

        return signal, reason

    def _calculate_ma(self, window: int) -> float:
        """
        Calculate simple moving average for the given window.

        Args:
            window (int): Number of periods to average

        Returns:
            float: Moving average value
        """
        # Take last window prices
        prices = list(self.__prices)[-window:]

        return sum(prices) / len(prices)

    def _detect_crossover(
        self, short_ma: float, long_ma: float
    ) -> tuple[Literal["BUY", "SELL", "HOLD"], str]:
        """
        Detect crossover between short and long moving averages.

        Args:
            short_ma (float): Current short-term MA
            long_ma (float): Current long-term MA

        Returns:
            tuple: (signal, reason)
        """
        # Bullish crossover: short MA crosses above long MA
        if self.__prev_short_ma <= self.__prev_long_ma and short_ma > long_ma:
            return (
                "BUY",
                f"Bullish crossover (short={short_ma:.2f} > long={long_ma:.2f})",
            )

        # Bearish crossover: short MA crosses below long MA
        elif self.__prev_short_ma >= self.__prev_long_ma and short_ma < long_ma:
            return (
                "SELL",
                f"Bearish crossover (short={short_ma:.2f} < long={long_ma:.2f})",
            )

        # No crossover
        else:
            return "HOLD", f"No crossover (short={short_ma:.2f}, long={long_ma:.2f})"


# Expose MAStrategy class to other modules
__all__ = ["MAStrategy"]
