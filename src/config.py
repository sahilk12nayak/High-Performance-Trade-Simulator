"""
Configuration settings for the Trade Simulator
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ExchangeConfig:
    """Configuration for an exchange"""
    name: str
    websocket_url: str
    available_pairs: List[str]
    fee_tiers: Dict[str, Dict[str, float]]
    
# Exchange configurations
EXCHANGES = {
    "OKX": ExchangeConfig(
        name="OKX",
        websocket_url="wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/",
        available_pairs=["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP", "XRP-USDT-SWAP"],
        fee_tiers={
            "VIP 0": {"maker": 0.0008, "taker": 0.0010},
            "VIP 1": {"maker": 0.0007, "taker": 0.0009},
            "VIP 2": {"maker": 0.0006, "taker": 0.0008},
            "VIP 3": {"maker": 0.0005, "taker": 0.0007},
            "VIP 4": {"maker": 0.0003, "taker": 0.0005},
            "VIP 5": {"maker": 0.0000, "taker": 0.0003},
        }
    )
}

# Default values for simulation parameters
DEFAULT_EXCHANGE = "OKX"
DEFAULT_PAIR = "BTC-USDT-SWAP"
DEFAULT_ORDER_TYPE = "market"
DEFAULT_QUANTITY = 100.0  # USD equivalent
DEFAULT_VOLATILITY = 0.02  # 2% daily volatility
DEFAULT_FEE_TIER = "VIP 0"

# UI Configuration
UI_REFRESH_RATE_MS = 100  # UI refresh rate in milliseconds
UI_WINDOW_TITLE = "High-Performance Trade Simulator"
UI_WINDOW_SIZE = (1200, 800)

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "trade_simulator.log"

# Performance benchmarking
ENABLE_BENCHMARKING = True
BENCHMARK_INTERVAL_SEC = 10  # Benchmark reporting interval in seconds