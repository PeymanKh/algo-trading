"""
Data Schemas

This module defines the data structures used throughout the application.
It includes two main schemas:
    1. Trade schema for Binance WebSocket trade streams
    2. Analytics schema for calculating trading statistics

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

from typing import Literal, List
from pydantic import BaseModel, Field


##################################################
################## Trade Schema ##################
##################################################
class Trade(BaseModel):
    """Trade data model for Binance WebSocket trade streams"""

    event_time: int = Field(..., description="Event timestamp in ms")
    symbol: str = Field(..., description="Trading pair")
    trade_id: int = Field(..., description="Unique trade ID")
    price: float = Field(..., description="Execution price")
    quantity: float = Field(..., description="Trade quantity")
    trade_time: int = Field(..., description="Trade execution timestamp in ms")
    trade_type: Literal["SELL", "BUY"] = Field(
        ..., description="Side of the trade (BUY or SELL)"
    )


##################################################
################ Analytics Schema ################
##################################################
class OHLC(BaseModel):
    """Open, High, Low, Close prices"""

    o: float = Field(default=0.0, description="Opening price")
    h: float = Field(default=0.0, description="Highest price")
    l: float = Field(default=float('inf'), description="Lowest price")
    c: float = Field(default=0.0, description="Closing price")


class PriceMetrics(BaseModel):
    """Price movement metrics"""

    range: float = Field(default=0.0, description="Price range")
    std: float = Field(default=0.0, description="Standard deviation")
    change_pct: float = Field(default=0.0, description="Price change percentage")


class Volume(BaseModel):
    """Volume split by trade type"""

    total: float = Field(default=0.0, description="Total volume")
    buy: float = Field(default=0.0, description="Buy volume")
    sell: float = Field(default=0.0, description="Sell volume")


class VolumeMetrics(BaseModel):
    """Base and quote volume"""

    base: Volume = Field(default=Volume(), description="Base asset volume")
    quote: Volume = Field(default=Volume(), description="Quote asset volume")


class ActivityMetrics(BaseModel):
    """Trading activity metrics"""

    total_trades: int = Field(default=0, description="Total trades")
    buy_trades: int = Field(default=0, description="Buy trades")
    sell_trades: int = Field(default=0, description="Sell trades")
    trades_per_sec: float = Field(default=0.0, description="Trades per second")
    buy_sell_ratio: float = Field(default=0.0, description="Buy/sell ratio")


class WindowAnalytics(BaseModel):
    """Analytics for a time window"""

    symbol: str = Field(default=None, description="Trading pair")
    prices: List[float] = Field(default_factory=list, description="List of prices")
    last_trade_time: int = Field(default=0, description="Last trade timestamp in ms")
    first_trade_time: int = Field(default=0, description="First trade timestamp in ms")
    ohlc: OHLC = Field(default_factory=OHLC)
    price_metrics: PriceMetrics = Field(default_factory=PriceMetrics)
    volume: VolumeMetrics = Field(default_factory=VolumeMetrics)
    activity: ActivityMetrics = Field(default_factory=ActivityMetrics)
