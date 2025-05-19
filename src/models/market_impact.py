"""
Market impact model for the Trade Simulator
"""
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MarketImpactModel:
    """Model for estimating market impact using Almgren-Chriss model"""
    
    def __init__(self):
        """Initialize the market impact model"""
        # Almgren-Chriss model parameters
        self.sigma = 0.0  # Market volatility (set dynamically)
        self.gamma = 0.1  # Market resilience parameter
        self.eta = 1.0    # Market depth parameter
        
        logger.info("Market impact model initialized")
    
    def calculate(self, quantity: float, price: float, volatility: float, orderbook_data: Dict[str, Any]) -> float:
        """Calculate expected market impact percentage using Almgren-Chriss model"""
        try:
            # Set volatility parameter
            self.sigma = volatility
            
            # Estimate market depth from orderbook
            self._estimate_market_parameters(orderbook_data)
            
            # Calculate temporary impact (immediate price movement)
            # I_temp = eta * sigma * sqrt(quantity / V)
            daily_volume = self._estimate_daily_volume(orderbook_data)
            quantity_ratio = quantity / daily_volume
            
            # Temporary impact as percentage
            temporary_impact = self.eta * self.sigma * np.sqrt(quantity_ratio)
            
            # Calculate permanent impact (lasting price change)
            # I_perm = gamma * sigma * quantity / V
            permanent_impact = self.gamma * self.sigma * quantity_ratio
            
            # Total impact as percentage
            total_impact = temporary_impact + permanent_impact
            
            # Convert to percentage
            impact_percentage = total_impact * 100
            
            return impact_percentage
        
        except Exception as e:
            logger.error(f"Error calculating market impact: {e}")
            return 0.01  # Default to 0.01% impact on error
    
    def _estimate_market_parameters(self, data: Dict[str, Any]) -> None:
        """Estimate market parameters from orderbook data"""
        # Estimate market depth parameter (eta)
        # Lower depth means higher eta (more impact)
        bid_depth = data["bid_depth"]
        ask_depth = data["ask_depth"]
        total_depth = bid_depth + ask_depth
        
        # Normalize depth to a reasonable range for eta
        if total_depth > 0:
            normalized_depth = min(1.0, 100 / total_depth)
            self.eta = 0.5 + normalized_depth  # Range: 0.5 to 1.5
        
        # Estimate market resilience (gamma)
        # Higher spread means lower resilience (higher gamma)
        spread_pct = data["spread_pct"]
        self.gamma = 0.1 + (spread_pct / 100)  # Base 0.1 plus spread contribution
    
    def _estimate_daily_volume(self, data: Dict[str, Any]) -> float:
        """Estimate daily trading volume from orderbook data"""
        # This is a simplified estimation
        # In a real system, you would use historical volume data
        
        # Use orderbook depth as a proxy for volume
        bid_depth = data["bid_depth"]
        ask_depth = data["ask_depth"]
        
        # Assume depth represents ~5% of daily volume
        estimated_volume = (bid_depth + ask_depth) * 20
        
        # Ensure minimum volume to avoid division by zero
        return max(estimated_volume, 1000)