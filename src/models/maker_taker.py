"""
Maker/Taker proportion model for the Trade Simulator
"""
import logging
import numpy as np
from typing import Dict, Any
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)

class MakerTakerModel:
    """Model for predicting maker/taker proportion"""
    
    def __init__(self):
        """Initialize the maker/taker model"""
        self.model = LogisticRegression()
        self.is_trained = False
        self.training_data_x = []
        self.training_data_y = []
        
        logger.info("Maker/Taker model initialized")
    
    def predict(self, data: Dict[str, Any]) -> float:
        """Predict maker proportion (0.0 to 1.0)"""
        try:
            # Extract features for prediction
            order_type = data["order_type"]
            quantity = data["quantity"]
            spread_pct = data["spread_pct"]
            imbalance = data["imbalance"]
            
            # For market orders, assume all taker
            if order_type == "market":
                maker_proportion = 0.0
            else:
                # For limit orders, use heuristic or model
                if self.is_trained:
                    features = self._extract_features(data)
                    maker_proportion = self.model.predict_proba([features])[0][1]
                else:
                    # Heuristic: higher spread and lower quantity favor maker orders
                    base_proportion = 0.5
                    spread_factor = min(0.3, spread_pct / 10)  # Higher spread -> more maker
                    quantity_factor = min(0.2, 10 / quantity)  # Lower quantity -> more maker
                    
                    maker_proportion = base_proportion + spread_factor + quantity_factor
                    maker_proportion = min(1.0, maker_proportion)
            
            # Collect training data
            self._collect_training_data(data, maker_proportion)
            
            return maker_proportion
        
        except Exception as e:
            logger.error(f"Error predicting maker/taker proportion: {e}")
            return 0.0  # Default to all taker on error
    
    def _collect_training_data(self, data: Dict[str, Any], observed_proportion: float) -> None:
        """Collect training data for logistic regression model"""
        features = self._extract_features(data)
        
        # Convert proportion to binary label (>0.5 = maker, <0.5 = taker)
        label = 1 if observed_proportion > 0.5 else 0
        
        self.training_data_x.append(features)
        self.training_data_y.append(label)
        
        # Train model when we have enough data
        if len(self.training_data_y) >= 100 and not self.is_trained:
            self._train_model()
        elif len(self.training_data_y) >= 500 and len(self.training_data_y) % 100 == 0:
            # Retrain periodically with more data
            self._train_model()
    
    def _extract_features(self, data: Dict[str, Any]) -> list:
        """Extract features for logistic regression model"""
        # Convert order type to numeric
        order_type_num = 0 if data["order_type"] == "market" else 1
        
        features = [
            order_type_num,
            data["quantity"],
            data["spread_pct"],
            data["imbalance"],
            data["depth_ratio"],
            data["volatility"]
        ]
        return features
    
    def _train_model(self) -> None:
        """Train the logistic regression model"""
        try:
            X = np.array(self.training_data_x)
            y = np.array(self.training_data_y)
            
            self.model.fit(X, y)
            self.is_trained = True
            
            logger.info(f"Trained maker/taker model with {len(y)} samples")
        except Exception as e:
            logger.error(f"Error training maker/taker model: {e}")