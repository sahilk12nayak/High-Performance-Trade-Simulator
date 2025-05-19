"""
Slippage model for the Trade Simulator
"""
import logging
import numpy as np
from typing import Dict, Any
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

class SlippageModel:
    """Model for estimating slippage based on orderbook data"""
    
    def __init__(self):
        """Initialize the slippage model"""
        self.model = LinearRegression()
        self.is_trained = False
        self.training_data_x = []
        self.training_data_y = []
        
        logger.info("Slippage model initialized")
    
    def calculate(self, data: Dict[str, Any]) -> float:
        """Calculate expected slippage percentage"""
        try:
            # Extract features for slippage calculation
            quantity = data["quantity"]
            mid_price = data["mid_price"]
            spread_pct = data["spread_pct"]
            imbalance = data["imbalance"]
            
            # Simple model: base slippage on spread and quantity
            base_slippage = spread_pct / 2  # Half the spread as base slippage
            
            # Adjust for quantity (larger orders have more slippage)
            quantity_factor = 0.01 * np.log1p(quantity / 100)  # Logarithmic scaling
            
            # Adjust for orderbook imbalance
            # If imbalance > 0.5, more bids than asks, so buying has more slippage
            # If imbalance < 0.5, more asks than bids, so selling has more slippage
            imbalance_factor = (imbalance - 0.5) * 0.5
            
            # Calculate final slippage
            slippage = base_slippage + (quantity_factor * (1 + imbalance_factor))
            
            # Collect training data for regression model
            self._collect_training_data(data, slippage)
            
            # Use regression model if trained
            if self.is_trained:
                features = self._extract_features(data)
                predicted_slippage = self.model.predict([features])[0]
                
                # Blend model prediction with heuristic calculation
                slippage = 0.7 * predicted_slippage + 0.3 * slippage
            
            return max(0.0, slippage)  # Ensure non-negative slippage
        
        except Exception as e:
            logger.error(f"Error calculating slippage: {e}")
            return 0.01  # Default to 0.01% slippage on error
    
    def _collect_training_data(self, data: Dict[str, Any], observed_slippage: float) -> None:
        """Collect training data for regression model"""
        features = self._extract_features(data)
        
        self.training_data_x.append(features)
        self.training_data_y.append(observed_slippage)
        
        # Train model when we have enough data
        if len(self.training_data_y) >= 100 and not self.is_trained:
            self._train_model()
        elif len(self.training_data_y) >= 500 and len(self.training_data_y) % 100 == 0:
            # Retrain periodically with more data
            self._train_model()
    
    def _extract_features(self, data: Dict[str, Any]) -> list:
        """Extract features for regression model"""
        features = [
            data["quantity"],
            data["spread_pct"],
            data["imbalance"],
            data["depth_ratio"],
            data["volatility"]
        ]
        return features
    
    def _train_model(self) -> None:
        """Train the regression model"""
        try:
            X = np.array(self.training_data_x)
            y = np.array(self.training_data_y)
            
            self.model.fit(X, y)
            self.is_trained = True
            
            logger.info(f"Trained slippage model with {len(y)} samples")
        except Exception as e:
            logger.error(f"Error training slippage model: {e}")