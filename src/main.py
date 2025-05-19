#!/usr/bin/env python3
"""
Trade Simulator - Main Entry Point
"""
import sys
import logging
from src.ui.app import TradeSimulatorApp
from src.utils.logging_config import setup_logging

def main():
    """Main entry point for the application"""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Trade Simulator")
    
    app = TradeSimulatorApp()
    app.run()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())