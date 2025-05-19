"""
Fee model for the Trade Simulator
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FeeModel:
    """Model for calculating trading fees"""
    
    def __init__(self):
        """Initialize the fee model"""
        self.maker_rate = 0.0008  # Default maker fee rate (0.08%)
        self.taker_rate = 0.0010  # Default taker fee rate (0.10%)
        
        logger.info("Fee model initialized")
    
    def set_fee_rates(self, maker_rate: float, taker_rate: float) -> None:
        """Set fee rates"""
        self.maker_rate = maker_rate
        self.taker_rate = taker_rate
        
        logger.info(f"Fee rates updated: maker={maker_rate}, taker={taker_rate}")
    
    def calculate(self, quantity: float, price: float, maker_proportion: float) -> float:
        """Calculate expected fees in USD"""
        try:
            # Calculate trade value
            trade_value = quantity
            
            # Calculate maker and taker portions
            maker_value = trade_value * maker_proportion
            taker_value = trade_value * (1 - maker_proportion)
            
            # Calculate fees
            maker_fee = maker_value * self.maker_rate
            taker_fee = taker_value * self.taker_rate
            
            total_fee = maker_fee + taker_fee
            
            return total_fee
        
        except Exception as e:
            logger.error(f"Error calculating fees: {e}")
            return 0.0  # Default to zero fees on error