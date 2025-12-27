"""
Volatility Breakout Strategy

This strategy generates trading signals based on sudden changes in price volatility.
High volatility often indicates strong price movements and potential trading opportunities.

Signal Logic:
    - BUY: When volatility spikes above threshold AND price is rising
    - SELL: When volatility spikes above threshold AND price is falling
    - HOLD: When volatility is normal or no clear direction

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import logging
from typing import Literal
from collections import deque
from statistics import stdev

from src.strategies.base_strategy import BaseStrategy
from src.utils.schema import WindowAnalytics

# Logger
logger = logging.getLogger(__name__)


class VolatilityStrategy(BaseStrategy):
    """
    Volatility Breakout Strategy.

    This strategy monitors rolling volatility (standard deviation of prices).
    When volatility exceeds a threshold, it generates signals based on the price direction.
    """

    def __init__(
            self,
            symbol: str,
            window: int = 20,
            threshold_multiplier: float = 2.0,
            data_dir: str = "signals"
    ) -> None:
        """
        Initialize Volatility Breakout Strategy.

        Args:
            symbol (str): Trading symbol to analyze
            window (int, optional): Number of periods for volatility calculation. Defaults to 20.
            threshold_multiplier (float, optional): Volatility spike threshold (e.g., 2.0 = 2x average). Defaults to 2.0.
            data_dir (str, optional): Directory to store signals. Defaults to "signals".

        Raises:
            ValueError: If threshold_multiplier <= 0
        """
        # Validation
        if threshold_multiplier <= 0:
            raise ValueError("threshold_multiplier must be positive")

        super().__init__(symbol, data_dir)

        self.__window = window
        self.__threshold_multiplier = threshold_multiplier

        # Store price history
        self.__prices = deque(maxlen=window)

        # Store volatility history to calculate average
        self.__volatilities = deque(maxlen=window)

        logger.info(
            f"Initialized VolatilityStrategy for {symbol}: "
            f"window={window}, threshold={threshold_multiplier}x"
        )

    def generate_signal(
            self, analytics: WindowAnalytics
    ) -> tuple[Literal["BUY", "SELL", "HOLD"], str]:
        """
        Generate trading signal based on volatility breakout.

        Args:
            analytics (WindowAnalytics): Market data for the current window

        Returns:
            tuple: (signal, reason)
        """
        # Add latest closing price
        current_price = analytics.ohlc.c
        self.__prices.append(current_price)

        # Wait until we have enough data
        if len(self.__prices) < self.__window:
            return (
                "HOLD",
                f"Not enough data for long Volatility Breakout ({self.__window} required)",
            )

        # Calculate current volatility (standard deviation)
        current_volatility = stdev(self.__prices)
        self.__volatilities.append(current_volatility)

        # Need at least 2 volatility readings to calculate average
        if len(self.__volatilities) < 2:
            return "HOLD", "Building volatility history"

        # Calculate average volatility
        avg_volatility = sum(self.__volatilities) / len(self.__volatilities)

        # Check if volatility spike occurred
        volatility_ratio = current_volatility / avg_volatility if avg_volatility > 0 else 0

        if volatility_ratio >= self.__threshold_multiplier:
            # Volatility spike detected so it checks the price direction
            signal, reason = self._check_price_direction(
                current_price,
                current_volatility,
                avg_volatility,
                volatility_ratio
            )
            return signal, reason

        else:
            # Normal volatility
            return (
                "HOLD",
                f"Normal volatility (current={current_volatility:.2f}, avg={avg_volatility:.2f}, ratio={volatility_ratio:.2f}x)"
            )

    def _check_price_direction(
            self,
            current_price: float,
            current_vol: float,
            avg_vol: float,
            vol_ratio: float
    ) -> tuple[Literal["BUY", "SELL", "HOLD"], str]:
        """
        Determine signal based on the price direction during volatility spike.

        Args:
            current_price (float): Latest price
            current_vol (float): Current volatility
            avg_vol (float): Average volatility
            vol_ratio (float): Ratio of current to average volatility

        Returns:
            tuple: (signal, reason)
        """
        # Compare current price to recent average (last 5 prices)
        recent_prices = list(self.__prices)[-5:]
        avg_recent_price = sum(recent_prices) / len(recent_prices)

        # Price rising during volatility spike (Bullish breakout)
        if current_price > avg_recent_price:
            return (
                "BUY",
                f"Bullish breakout (vol spike {vol_ratio:.2f}x, price={current_price:.2f} > avg={avg_recent_price:.2f})"
            )

        # Price falling during volatility spike (Bearish breakout)
        elif current_price < avg_recent_price:
            return (
                "SELL",
                f"Bearish breakout (vol spike {vol_ratio:.2f}x, price={current_price:.2f} < avg={avg_recent_price:.2f})"
            )

        # Price flat during volatility spike → Wait
        else:
            return (
                "HOLD",
                f"Volatility spike but no clear direction (vol={vol_ratio:.2f}x)"
            )


# Expose VolatilityStrategy class to other modules
__all__ = ["VolatilityStrategy"]
