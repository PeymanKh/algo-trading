"""
WebSocket Client for Binance Trade Streams

This module connects to Binance WebSocket API and streams real-time trade data.

Author: Peyman Khodabandehlouei
Last Update: 27-12-2025
"""

import json
import logging
import asyncio

import websockets
from typing import List

from src.utils.schema import Trade
from src.utils.memory import get_memory
from src.configs.sys_config import config
from src.utils.analytics import AnalyticsWorker
from src.configs.logging_config import setup_logging


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def connect_and_subscribe(batch_id: int, symbols: List[str]):

    # Construct subscribe message
    params = [f"{symbol}@trade" for symbol in symbols]
    subscribe_msg = {"method": "SUBSCRIBE", "params": params, "id": batch_id}

    memory = get_memory()

    try:
        async with websockets.connect(config.binance_ws_url) as ws:
            logger.info(
                f"[Batch {batch_id}] Connected. Subscribing to {len(symbols)} streams..."
            )

            await ws.send(json.dumps(subscribe_msg))

            while True:
                try:
                    message = await ws.recv()
                    data = json.loads(message)

                    if "data" in data:

                        event = data["data"]

                        try:
                            trade = Trade(
                                event_time=event["E"],
                                symbol=event["s"],
                                trade_id=event["t"],
                                price=float(event["p"]),
                                quantity=float(event["q"]),
                                trade_time=event["T"],
                                trade_type="SELL" if event["m"] else "BUY",
                            )

                            memory.add_trade(trade)
                            # logger.info(f"{trade.model_dump_json()}")

                        except (KeyError, ValueError, TypeError) as e:
                            logger.warning(
                                f"Failed to parse trade: {e}, event: {event}"
                            )
                            continue

                    elif "result" in data:
                        logger.info(f"Subscription was successful.")

                    else:
                        logger.warning(f"Unknown message: {data}")

                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Connection closed. Reconnecting...")
                    break

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


async def main():
    if not config.symbols:
        logger.error("No symbols found. Exiting...")
        return

    chunks = [
        config.symbols[i : i + config.symbols_per_connection]
        for i in range(0, len(config.symbols), config.symbols_per_connection)
    ]

    logger.info(f"Spawning {len(chunks)} WebSocket connections...")

    workers = []
    for symbol in config.symbols:
        worker = AnalyticsWorker(symbol=symbol.upper())
        worker.start()
        workers.append(worker)

    logger.info(f"Started {len(workers)} analytics workers")

    tasks = []
    for i, chunk in enumerate(chunks):
        tasks.append(connect_and_subscribe(i + 1, chunk))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nStopping...")
