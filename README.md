# High-Performance-Trade-Simulator

A real-time trade simulator that leverages WebSocket market data to estimate transaction costs and market impact for cryptocurrency exchanges.

## Overview

This project implements a high-performance trade simulator that connects to WebSocket endpoints streaming L2 orderbook data from cryptocurrency exchanges. The simulator processes this data in real-time to estimate various trading costs and market impact metrics using financial models.

## Features

- Real-time connection to OKX exchange WebSocket feeds
- Full L2 orderbook processing
- Interactive UI with input parameters and output metrics
- Implementation of financial models:
  - Slippage estimation using linear regression
  - Fee calculation based on exchange fee tiers
  - Market impact calculation using Almgren-Chriss model
  - Maker/Taker proportion prediction using logistic regression
- Performance benchmarking and optimization

## Requirements

- Python 3.8+
- PyQt5 for the user interface
- NumPy, SciPy, and scikit-learn for mathematical models
- websockets library for WebSocket connections
