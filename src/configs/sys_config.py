"""
Application configurations

This module contains all the configurations for the application.

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import sys
import logging
from typing import List
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemConfig(BaseSettings):
    """System configurations."""

    # Logging Configurations
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default='{"ts": "%(asctime)s", "logger": "%(name)s", "msg": "%(message)s"}',
        description="Log message format string",
    )

    # WebSocket Configuration
    binance_ws_url: str = Field(
        default="wss://stream.binance.com:9443/stream",
        description="Binance WebSocket URL",
    )
    symbols_per_connection: int = Field(
        default=20, description="Number of symbols per WebSocket connection"
    )

    # Symbols to track
    symbols: List[str] = Field(
        default=[
            "btcusdt",
            "ethusdt",
            "solusdt",
        ],
        description="List of symbols to track",
    )

    # Memory Configuration
    max_trades_per_symbol: int = Field(
        default=10_000, description="Memory's maximum trades per symbol"
    )

    # Reconnection Configuration
    max_reconnect_attempts: int = Field(
        default=10, description="Maximum reconnection attempts before giving up"
    )
    initial_reconnect_delay: int = Field(
        default=1, description="Initial delay in seconds for reconnection backoff"
    )
    max_reconnect_delay: int = Field(
        default=60, description="Maximum delay in seconds for reconnection backoff"
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


try:
    config = SystemConfig()
except Exception as e:
    logging.error(f"Failed to load config variables: {e}")
    sys.exit(1)


# Public API
__all__ = ["config", "SystemConfig"]
