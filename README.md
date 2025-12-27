# Real-Time Algorithmic Trading

This project implements real-time market data analysis system. 
It subscribes to Binane WebSocket, saves trades stream to a custom thread-safe in-memory data structure, and analyzes trade data using functional programming principles and concurrent processing.

---

## Project Structure
```terminaloutput
.
├── src
│    ├── configs
│    │    ├── logging_config.py
│    │    └── sys_config.py
│    │
│    ├── strategies
│    │    ├── base_strategy.py
│    │    ├── ma_crossover.py
│    │    └── volatility_strategy.py
│    │
│    ├── utils
│    │    ├── analytics.py
│    │    ├── memory.py
│    │    └── schema.py
│    │
│    └── main.py 
│
├── .enc.example
├── .gitignore
├── README.md
└── Requirements.txt
```
- [logging_config.py](src/configs/logging_config.py): Logging setup for the application.
- [sys_config.py](src/configs/sys_config.py): Application configurations implemented using [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). It includes desired symbols, Binance WebSocket URL, and other necessary configurations.
- [base.py](src/strategies/base_strategy.py): Defines `BaseStrategy` abstract class which is an abstract implementation for all trading strategies. Handles signal generation, CSV logging, and basic performance statistics.
- [ma_crossover.py](src/strategies/ma_crossover.py): Implements `MAStrategy` class for moving average crossover trading strategy. Generates BUY signals when short-term MA crosses above long-term MA, and SELL signals on bearish crossovers.
- [volatility_breakout.py](src/strategies/volatility_breakout.py): Implements `VolatilityStrategy` class for volatility breakout trading. Detects price volatility spikes and generates signals based on the price direction during high volatility periods.
- [analytics.py](src/utils/analytics.py): Implements `AnalyticsWorker` class which is a background worker for periodic analysis of trade data. This class uses functional programming for efficient CPU-bound analysis.
- [memory.py](src/utils/memory.py): Implements `Memory` class which is a thread-safe in-memory data structure for storing and accessing trade data. This class uses `threading.Lock()` for thread-safe reads and writes, `collections.deque` to avoid infinity memory growth, and exposes a single instance of `Memory` class to other modules in the application using singleton design pattern.
- [schema.py](src/utils/schema.py): Defines `Trade` data model which represents a single trade event from Binance WebSocket and `WindowAnalytics` which represents the analysis of a single rolling window of trade data.
- [main.py](src/main.py): Main entry point for the application including Binance WebSocket subscription and application's business logic.

---
## Quick Start

### 1. Clone and Setup

```bash

git clone https://github.com/PeymanKh/algo-trading.git
cd algo-trading

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Copy .env.example File
This application by default subscribes to BTCUSDT, ETHUSDT, and SOLUSDT symbols. You can change them in .env file after copying .env.example
```bash

cp .env.example .env
# Next read .env file to understand application configurations.
```

### 3. Run Application
By running this code, the application will subscribe to Binance WebSocket and run perform analysis on 30-second rolling window.
```bash

python3 -m src.main
```

