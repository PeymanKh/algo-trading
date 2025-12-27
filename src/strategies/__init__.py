"""
Trading Strategies Module

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

from src.strategies.base_strategy import BaseStrategy
from src.strategies.ma_crossover import MAStrategy
from src.strategies.volatility_breakout import VolatilityStrategy

__all__ = ["BaseStrategy", "MAStrategy", "VolatilityStrategy"]
