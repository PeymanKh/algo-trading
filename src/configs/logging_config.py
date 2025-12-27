"""
Logging Configuration

This module provides logging setup for the application.
It configures logging based on settings from sys_config.py.

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import logging

from src.configs.sys_config import config


def setup_logging() -> None:
    """Configure application-wide logging."""

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=config.log_format,
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # Reduce noise from external libraries
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
