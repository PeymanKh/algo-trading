"""
Analytics worker

This module implements a background worker class that periodically reads from shared Memory
and calculates trading statistics using thread-based concurrency.

Features:
    - Thread-safe concurrency
    - Rolling time window analysis (30 seconds by default)
    - Price metrics (OHLC, range, standard deviation, change percentage)
    - Volume metrics (base and quote)
    - Activity metrics (total trades, buy/sell trades, trades per second)

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import time
import logging
import threading
from typing import List
from functools import reduce
from statistics import stdev

from src.utils.memory import get_memory
from src.utils.schema import Trade, WindowAnalytics

# Logger
logger = logging.getLogger(__name__)


class AnalyticsWorker:
    """
    Background worker for trade analysis.

    This class implements a thread-based worker that periodically queries the shared
    Memory instance for recent trades and calculates market statistics.
    """

    def __init__(self, symbol: str, window_size: int = 5) -> None:
        """
        Initialize the analytics worker for a specific trading symbol.

        Args:
            symbol (str): Trading symbol to analyze
            window_size (int, optional): Rolling window duration in seconds for statistical analysis. Defaults to 30.

        Raises:
            ValueError: If symbol is not a string, or window_size is not a positive integer.
        """
        # Validation
        if not isinstance(symbol, str):
            raise ValueError("symbol must be a string")
        if not isinstance(window_size, int) or window_size <= 0:
            raise ValueError("window_size must be a positive integer")

        self.__symbol = symbol
        self.__thread = None
        self.__running = False
        self.__window_size = window_size
        self.__memory = get_memory()

    def start(self) -> None:
        """
        Start the analytics worker thread.

        Creates and starts a thread that continuously performs analysis at
        intervals equal to the configured window size.
        """
        self.__running = True
        self.__thread = threading.Thread(
            target=self._run,
            name=f"{self.__symbol}-AnalyticsWorker",
            daemon=True,
        )
        self.__thread.start()
        logger.info(f"{self.__symbol} AnalyticsWorker started...")

    def _run(self) -> None:
        """
        Main worker loop.

        Continuously retrieves trades from the last N seconds (window_size) from
        shared memory, performs comprehensive analysis, and sleeps before the next
        iteration.

        Note:
            This is a private method and should not be called directly.
        """
        while self.__running:
            try:
                # Access trades
                trades = self.__memory.get_trades_last_n_second(
                    self.__symbol, self.__window_size
                )

                # Perform analysis
                self._analyze_trades(trades)

                # Wait before next iteration
                time.sleep(self.__window_size)

            except Exception as e:
                logger.error(
                    f"{self.__symbol} AnalyticsWorker error: {e}", exc_info=True
                )
                time.sleep(self.__window_size)

    def _analyze_trades(self, trades: List[Trade]) -> None:
        """
        Perform market analysis on a list of trades. To enhance efficiency of this method,
        functional programming method has been used to overcome multiple Trade list iterations.

        Computes multiple categories of trading metrics:
            - **OHLC**: Open, High, Low, Close prices for the window
            - **Price Metrics**: Range, standard deviation, percentage change
            - **Volume**: Base and quote currency volumes split by buy/sell side
            - **Activity**: Trade counts, buy/sell ratio, trades per second

        Args:
            trades (List[Trade]): List of trades within the analysis window.
        """
        # Overcome crash
        if not trades:
            return

        def _reduce_trades(analysis: WindowAnalytics, trade: Trade) -> WindowAnalytics:
            """Pure function to reduce a list of trades into a WindowAnalytics object."""

            # Update OHLC
            if analysis.activity.total_trades == 0:
                analysis.ohlc.o = trade.price
                analysis.first_trade_time = trade.trade_time
            analysis.ohlc.h = max(trade.price, analysis.ohlc.h)
            analysis.ohlc.l = min(trade.price, analysis.ohlc.l)
            analysis.ohlc.c = trade.price   # Last price would stay here
            analysis.last_trade_time = trade.trade_time  # Last trade.trade_time would stay here

            # Update volume
            if trade.trade_type == "BUY":
                analysis.volume.base.buy += trade.quantity
                analysis.volume.quote.buy += trade.price * trade.quantity
                analysis.activity.buy_trades += 1
            else:
                analysis.volume.base.sell += trade.quantity
                analysis.volume.quote.sell += trade.price * trade.quantity
                analysis.activity.sell_trades += 1

            # Add price to the list for future analysis
            analysis.prices.append(trade.price)
            analysis.activity.total_trades += 1

            return analysis

        # Functional reduce
        analytics = reduce(_reduce_trades, trades, WindowAnalytics())

        # Compute remaining metrics after reduce function
        analytics.symbol = self.__symbol
        analytics.price_metrics.range = round(analytics.ohlc.h - analytics.ohlc.l, 8)
        analytics.price_metrics.std = round(stdev(analytics.prices) if len(analytics.prices) > 1 else 0.0, 8)
        analytics.price_metrics.change_pct = round(((analytics.ohlc.c - analytics.ohlc.o) / analytics.ohlc.o) * 100, 8)

        analytics.volume.base.total = round(analytics.volume.base.buy + analytics.volume.base.sell, 8)
        analytics.volume.quote.total = round(analytics.volume.quote.buy + analytics.volume.quote.sell, 8)

        time_span_ms = analytics.last_trade_time - analytics.first_trade_time
        time_span_sec = time_span_ms / 1000.0 if time_span_ms > 0 else 1.0
        analytics.activity.trades_per_sec = round(analytics.activity.total_trades / time_span_sec, 3)
        analytics.activity.buy_sell_ratio = round(analytics.activity.buy_trades / analytics.activity.total_trades, 3)

        logger.info(analytics.model_dump(exclude={"prices", "last_trade_time", "first_trade_time"}))
