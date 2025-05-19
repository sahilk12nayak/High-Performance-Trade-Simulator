"""
Trade Simulator core implementation
"""
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

from src.data.orderbook import OrderBook
from src.models.slippage import SlippageModel
from src.models.fees import FeeModel
from src.models.market_impact import MarketImpactModel
from src.models.maker_taker import MakerTakerModel
from src.config import EXCHANGES, DEFAULT_EXCHANGE, DEFAULT_PAIR, DEFAULT_ORDER_TYPE, DEFAULT_QUANTITY, DEFAULT_VOLATILITY, DEFAULT_FEE_TIER

logger = logging.getLogger(__name__)

class TradeSimulator:
    """Core trade simulator implementation"""
    
    def __init__(self):
        """Initialize the trade simulator"""
        # Parameters
        self.exchange = DEFAULT_EXCHANGE
        self.pair = DEFAULT_PAIR
        self.order_type = DEFAULT_ORDER_TYPE
        self.quantity = DEFAULT_QUANTITY
        self.volatility = DEFAULT_VOLATILITY
        self.fee_tier = DEFAULT_FEE_TIER
        
        # Models
        self.orderbook = OrderBook()
        self.slippage_model = SlippageModel()
        self.fee_model = FeeModel()
        self.market_impact_model = MarketImpactModel()
        self.maker_taker_model = MakerTakerModel()
        
        # Performance metrics
        self.latency_history = []
        self.start_time = time.time()
        self.message_count = 0
        self.last_update_time = 0
        
        # Results
        self.slippage = 0.0
        self.fees = 0.0
        self.market_impact = 0.0
        self.net_cost = 0.0
        self.maker_proportion = 0.0
        
        logger.info("Trade simulator initialized")
    
    def set_parameters(self, exchange: str, pair: str, order_type: str, 
                      quantity: float, volatility: float, fee_tier: str) -> None:
        """Set simulation parameters"""
        self.exchange = exchange
        self.pair = pair
        self.order_type = order_type
        self.quantity = quantity
        self.volatility = volatility
        self.fee_tier = fee_tier
        
        # Update fee model with new fee tier
        if exchange in EXCHANGES and fee_tier in EXCHANGES[exchange].fee_tiers:
            self.fee_model.set_fee_rates(
                maker_rate=EXCHANGES[exchange].fee_tiers[fee_tier]["maker"],
                taker_rate=EXCHANGES[exchange].fee_tiers[fee_tier]["taker"]
            )
        
        logger.info(f"Parameters updated: {exchange}, {pair}, {order_type}, {quantity}, {volatility}, {fee_tier}")
    
    def process_orderbook(self, data: Dict[str, Any]) -> None:
        """Process orderbook data and update simulation"""
        start_time = time.time()
        
        try:
            # Update orderbook
            self.orderbook.update(data)
            
            # Update message statistics
            self.message_count += 1
            self.last_update_time = start_time
            
            # Run simulation models
            self._run_models()
            
            # Calculate processing latency
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.update_latency(latency)
            
            if self.message_count % 100 == 0:
                logger.debug(f"Processed {self.message_count} orderbook updates, latest latency: {latency:.2f} ms")
        
        except Exception as e:
            logger.error(f"Error processing orderbook: {e}")
    
    def _run_models(self) -> None:
        """Run all simulation models"""
        if not self.has_data():
            return
        
        # Get orderbook data for models
        data = self.orderbook.get_data_for_models()
        
        # Add simulation parameters to data
        data["quantity"] = self.quantity
        data["volatility"] = self.volatility
        data["order_type"] = self.order_type
        
        # Run models
        self.slippage = self.slippage_model.calculate(data)
        self.maker_proportion = self.maker_taker_model.predict(data)
        self.fees = self.fee_model.calculate(
            quantity=self.quantity,
            price=data["mid_price"],
            maker_proportion=self.maker_proportion
        )
        self.market_impact = self.market_impact_model.calculate(
            quantity=self.quantity,
            price=data["mid_price"],
            volatility=self.volatility,
            orderbook_data=data
        )
        
        # Calculate net cost
        mid_price = data["mid_price"]
        slippage_cost = (self.slippage / 100) * self.quantity
        impact_cost = (self.market_impact / 100) * self.quantity
        self.net_cost = slippage_cost + self.fees + impact_cost
    
    def update_latency(self, latency: float) -> None:
        """Update latency history"""
        self.latency_history.append(latency)
        
        # Keep only the last 100 measurements
        if len(self.latency_history) > 100:
            self.latency_history.pop(0)
    
    def has_data(self) -> bool:
        """Check if simulator has orderbook data"""
        return len(self.orderbook.bids) > 0 and len(self.orderbook.asks) > 0
    
    def get_orderbook(self) -> Dict[str, List[Tuple[str, str]]]:
        """Get current orderbook data"""
        return {
            "bids": self.orderbook.bids,
            "asks": self.orderbook.asks
        }
    
    def get_mid_price(self) -> float:
        """Get current mid price"""
        return self.orderbook.get_mid_price() or 0.0
    
    def get_slippage(self) -> float:
        """Get expected slippage percentage"""
        return self.slippage
    
    def get_fees(self) -> float:
        """Get expected fees in USD"""
        return self.fees
    
    def get_market_impact(self) -> float:
        """Get expected market impact percentage"""
        return self.market_impact
    
    def get_net_cost(self) -> float:
        """Get net cost in USD"""
        return self.net_cost
    
    def get_maker_proportion(self) -> float:
        """Get maker proportion (0.0 to 1.0)"""
        return self.maker_proportion
    
    def get_latency(self) -> float:
        """Get average processing latency in milliseconds"""
        if not self.latency_history:
            return 0.0
        return sum(self.latency_history) / len(self.latency_history)
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return self.message_count
    
    def get_processing_rate(self) -> float:
        """Get message processing rate (messages per second)"""
        elapsed_time = time.time() - self.start_time
        if elapsed_time <= 0:
            return 0.0
        return self.message_count / elapsed_time