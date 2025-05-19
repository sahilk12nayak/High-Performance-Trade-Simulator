"""
Orderbook processing for the Trade Simulator
"""
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

logger = logging.getLogger(__name__)

class OrderBook:
    """Processes and maintains the order book state"""
    
    def __init__(self):
        """Initialize the order book"""
        self.bids: List[Tuple[str, str]] = []
        self.asks: List[Tuple[str, str]] = []
        self.timestamp: str = ""
        self.exchange: str = ""
        self.symbol: str = ""
        self.last_update_time: float = 0
        self.update_count: int = 0
        
        logger.info("OrderBook initialized")
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update the order book with new data"""
        start_time = time.time()
        
        try:
            self.timestamp = data.get("timestamp", "")
            self.exchange = data.get("exchange", "")
            self.symbol = data.get("symbol", "")
            
            # Update bids and asks
            if "bids" in data:
                self.bids = data["bids"]
            if "asks" in data:
                self.asks = data["asks"]
            
            # Sort bids (descending) and asks (ascending)
            self.bids = sorted(self.bids, key=lambda x: float(x[0]), reverse=True)
            self.asks = sorted(self.asks, key=lambda x: float(x[0]))
            
            # Update statistics
            self.last_update_time = start_time
            self.update_count += 1
            
            if self.update_count % 100 == 0:
                logger.debug(f"Updated orderbook {self.update_count} times for {self.symbol}")
        
        except Exception as e:
            logger.error(f"Error updating orderbook: {e}")
    
    def get_mid_price(self) -> Optional[float]:
        """Get the mid price from the order book"""
        if not self.bids or not self.asks:
            return None
        
        best_bid = float(self.bids[0][0])
        best_ask = float(self.asks[0][0])
        
        return (best_bid + best_ask) / 2
    
    def get_spread(self) -> Optional[float]:
        """Get the spread from the order book"""
        if not self.bids or not self.asks:
            return None
        
        best_bid = float(self.bids[0][0])
        best_ask = float(self.asks[0][0])
        
        return best_ask - best_bid
    
    def get_spread_percentage(self) -> Optional[float]:
        """Get the spread as a percentage of the mid price"""
        mid_price = self.get_mid_price()
        spread = self.get_spread()
        
        if mid_price is None or spread is None:
            return None
        
        return (spread / mid_price) * 100
    
    def get_depth(self, price_levels: int = 10) -> Dict[str, float]:
        """Get the depth at various price levels"""
        depth = {"bids": 0.0, "asks": 0.0}
        
        # Calculate bid depth
        for i, (price, size) in enumerate(self.bids):
            if i >= price_levels:
                break
            depth["bids"] += float(size)
        
        # Calculate ask depth
        for i, (price, size) in enumerate(self.asks):
            if i >= price_levels:
                break
            depth["asks"] += float(size)
        
        return depth
    
    def get_vwap(self, quantity: float) -> Dict[str, float]:
        """Calculate Volume Weighted Average Price for a given quantity"""
        result = {"bid_vwap": 0.0, "ask_vwap": 0.0}
        
        # Calculate bid VWAP (for selling)
        remaining_qty = quantity
        total_cost = 0.0
        
        for price, size in self.bids:
            price_float = float(price)
            size_float = float(size)
            
            if remaining_qty <= 0:
                break
                
            executed_qty = min(remaining_qty, size_float)
            total_cost += executed_qty * price_float
            remaining_qty -= executed_qty
        
        if quantity > remaining_qty:
            result["bid_vwap"] = total_cost / (quantity - remaining_qty)
        
        # Calculate ask VWAP (for buying)
        remaining_qty = quantity
        total_cost = 0.0
        
        for price, size in self.asks:
            price_float = float(price)
            size_float = float(size)
            
            if remaining_qty <= 0:
                break
                
            executed_qty = min(remaining_qty, size_float)
            total_cost += executed_qty * price_float
            remaining_qty -= executed_qty
        
        if quantity > remaining_qty:
            result["ask_vwap"] = total_cost / (quantity - remaining_qty)
        
        return result
    
    def get_orderbook_imbalance(self) -> float:
        """Calculate orderbook imbalance (bid volume / total volume)"""
        depth = self.get_depth(price_levels=5)
        total_volume = depth["bids"] + depth["asks"]
        
        if total_volume == 0:
            return 0.5  # Neutral if no volume
        
        return depth["bids"] / total_volume
    
    def get_data_for_models(self) -> Dict[str, Any]:
        """Get processed orderbook data for model inputs"""
        data = {}
        
        # Basic metrics
        data["mid_price"] = self.get_mid_price() or 0.0
        data["spread"] = self.get_spread() or 0.0
        data["spread_pct"] = self.get_spread_percentage() or 0.0
        
        # Depth metrics
        depth = self.get_depth(price_levels=5)
        data["bid_depth"] = depth["bids"]
        data["ask_depth"] = depth["asks"]
        data["depth_ratio"] = depth["bids"] / depth["asks"] if depth["asks"] > 0 else 1.0
        
        # Imbalance
        data["imbalance"] = self.get_orderbook_imbalance()
        
        # Price levels
        if self.bids and self.asks:
            data["best_bid"] = float(self.bids[0][0])
            data["best_ask"] = float(self.asks[0][0])
            
            # Calculate price impact for different sizes
            for size in [1, 5, 10, 50, 100]:
                vwap = self.get_vwap(size)
                data[f"bid_vwap_{size}"] = vwap["bid_vwap"]
                data[f"ask_vwap_{size}"] = vwap["ask_vwap"]
        
        return data