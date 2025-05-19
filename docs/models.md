# Financial Models Documentation

This document provides detailed information about the financial models used in the Trade Simulator.

## Slippage Model

### Overview

The slippage model estimates the expected price slippage for a given order size. Slippage is the difference between the expected execution price and the actual execution price.

### Implementation

The model uses a hybrid approach combining heuristic calculation and machine learning:

1. **Base Calculation**:
   - Base slippage = (Spread / 2)
   - Quantity adjustment = 0.01 * log(quantity / 100)
   - Imbalance adjustment = (imbalance - 0.5) * 0.5
   - Initial slippage = Base + (Quantity adjustment * (1 + Imbalance adjustment))

2. **Regression Model**:
   - Features: quantity, spread percentage, orderbook imbalance, depth ratio, volatility
   - Target: observed slippage
   - Algorithm: Linear Regression
   - Training: Online learning with periodic retraining

3. **Final Prediction**:
   - Weighted average of heuristic and regression model predictions
   - weight_heuristic = 0.3, weight_model = 0.7

### Validation

The model is continuously validated against actual market data. The regression component improves over time as it learns from more observations.

## Fee Model

### Overview

The fee model calculates expected trading fees based on exchange fee tiers and execution characteristics.

### Implementation

1. **Inputs**:
   - Order quantity (in USD)
   - Current price
   - Maker/taker proportion
   - Exchange fee rates (from fee tier)

2. **Calculation**:
   - Maker value = Order value * Maker proportion
   - Taker value = Order value * (1 - Maker proportion)
   - Maker fee = Maker value * Maker fee rate
   - Taker fee = Taker value * Taker fee rate
   - Total fee = Maker fee + Taker fee

### Fee Tiers

The model supports different fee tiers based on exchange documentation. For OKX:

| Tier   | Maker Fee | Taker Fee |
|--------|-----------|-----------|
| VIP 0  | 0.080%    | 0.100%    |
| VIP 1  | 0.070%    | 0.090%    |
| VIP 2  | 0.060%    | 0.080%    |
| VIP 3  | 0.050%    | 0.070%    |
| VIP 4  | 0.030%    | 0.050%    |
| VIP 5  | 0.000%    | 0.030%    |

## Market Impact Model (Almgren-Chriss)

### Overview

The market impact model implements the Almgren-Chriss model to estimate how much an order will move the market price.

### Theoretical Background

The Almgren-Chriss model divides market impact into two components:

1. **Temporary Impact**: Immediate price movement during execution that recovers after the order is completed
2. **Permanent Impact**: Lasting price change that remains after the order is completed

The model is based on the following equations:

- Temporary Impact: I_temp = η * σ * sqrt(q / V)
- Permanent Impact: I_perm = γ * σ * (q / V)
- Total Impact: I_total = I_temp + I_perm

Where:
- η (eta): Market depth parameter
- γ (gamma): Market resilience parameter
- σ (sigma): Market volatility
- q: Order quantity
- V: Daily trading volume

### Implementation

1. **Parameter Estimation**:
   - Volatility (σ): Set from input parameter
   - Market depth (η): Estimated from orderbook depth
   - Market resilience (γ): Estimated from spread and volatility

2. **Volume Estimation**:
   - Daily volume is estimated from orderbook depth
   - Assumption: Visible depth represents ~5% of daily volume

3. **Impact Calculation**:
   - Calculate temporary and permanent impact components
   - Convert to percentage of price

### Limitations

- The model assumes linear permanent impact and square-root temporary impact
- Volume estimation is simplified and could be improved with historical data
- Parameters are estimated from limited orderbook data

## Maker/Taker Model

### Overview

The maker/taker model predicts what proportion of an order will be executed as maker vs. taker orders.

### Implementation

1. **Market Orders**:
   - For market orders, assumes 100% taker execution

2. **Limit Orders**:
   - Initial heuristic:
     - Base proportion = 0.5
     - Spread adjustment = min(0.3, spread_pct / 10)
     - Quantity adjustment = min(0.2, 10 / quantity)
     - Maker proportion = Base + Spread adjustment + Quantity adjustment

3. **Regression Model**:
   - Features: order type, quantity, spread percentage, imbalance, depth ratio, volatility
   - Target: binary classification (>0.5 maker, <0.5 taker)
   - Algorithm: Logistic Regression
   - Output: Probability of maker execution

### Training

The model is trained online using observed execution data. As more trades are simulated, the model improves its predictions.