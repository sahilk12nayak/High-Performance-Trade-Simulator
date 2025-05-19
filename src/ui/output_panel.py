"""
Output panel for the Trade Simulator
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, 
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

logger = logging.getLogger(__name__)

class OutputPanel(QWidget):
    """Output panel widget for simulation results"""
    
    def __init__(self, simulator):
        """Initialize the output panel"""
        super().__init__()
        self.simulator = simulator
        
        self.init_ui()
        logger.info("Output panel initialized")
    
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Output Parameters")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Results group
        results_group = QGroupBox("Simulation Results")
        results_layout = QGridLayout()
        
        # Create labels for results
        self.create_result_labels(results_layout)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Orderbook visualization
        orderbook_group = QGroupBox("Orderbook Visualization")
        orderbook_layout = QVBoxLayout()
        
        # Create orderbook table
        self.orderbook_table = QTableWidget(20, 3)  # 20 rows, 3 columns
        self.orderbook_table.setHorizontalHeaderLabels(["Bids", "Price", "Asks"])
        self.orderbook_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orderbook_table.verticalHeader().setVisible(False)
        orderbook_layout.addWidget(self.orderbook_table)
        
        orderbook_group.setLayout(orderbook_layout)
        layout.addWidget(orderbook_group)
        
        # Performance metrics
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QGridLayout()
        
        # Create labels for performance metrics
        self.create_performance_labels(perf_layout)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
    
    def create_result_labels(self, layout):
        """Create labels for simulation results"""
        # Create label pairs (name and value)
        row = 0
        
        # Expected Slippage
        layout.addWidget(QLabel("Expected Slippage:"), row, 0)
        self.slippage_label = QLabel("0.00%")
        layout.addWidget(self.slippage_label, row, 1)
        row += 1
        
        # Expected Fees
        layout.addWidget(QLabel("Expected Fees:"), row, 0)
        self.fees_label = QLabel("0.00 USD")
        layout.addWidget(self.fees_label, row, 1)
        row += 1
        
        # Expected Market Impact
        layout.addWidget(QLabel("Expected Market Impact:"), row, 0)
        self.impact_label = QLabel("0.00%")
        layout.addWidget(self.impact_label, row, 1)
        row += 1
        
        # Net Cost
        layout.addWidget(QLabel("Net Cost:"), row, 0)
        self.net_cost_label = QLabel("0.00 USD")
        layout.addWidget(self.net_cost_label, row, 1)
        row += 1
        
        # Maker/Taker Proportion
        layout.addWidget(QLabel("Maker/Taker Proportion:"), row, 0)
        self.maker_taker_label = QLabel("0% / 100%")
        layout.addWidget(self.maker_taker_label, row, 1)
    
    def create_performance_labels(self, layout):
        """Create labels for performance metrics"""
        # Create label pairs (name and value)
        row = 0
        
        # Internal Latency
        layout.addWidget(QLabel("Internal Latency:"), row, 0)
        self.latency_label = QLabel("0.00 ms")
        layout.addWidget(self.latency_label, row, 1)
        row += 1
        
        # Messages Processed
        layout.addWidget(QLabel("Messages Processed:"), row, 0)
        self.messages_label = QLabel("0")
        layout.addWidget(self.messages_label, row, 1)
        row += 1
        
        # Processing Rate
        layout.addWidget(QLabel("Processing Rate:"), row, 0)
        self.rate_label = QLabel("0 msgs/sec")
        layout.addWidget(self.rate_label, row, 1)
    
    def update_display(self):
        """Update the display with latest simulation results"""
        if not self.simulator.has_data():
            return
        
        # Update result labels
        self.slippage_label.setText(f"{self.simulator.get_slippage():.4f}%")
        self.fees_label.setText(f"{self.simulator.get_fees():.4f} USD")
        self.impact_label.setText(f"{self.simulator.get_market_impact():.4f}%")
        self.net_cost_label.setText(f"{self.simulator.get_net_cost():.4f} USD")
        
        maker_pct = self.simulator.get_maker_proportion() * 100
        taker_pct = 100 - maker_pct
        self.maker_taker_label.setText(f"{maker_pct:.1f}% / {taker_pct:.1f}%")
        
        # Update performance labels
        self.latency_label.setText(f"{self.simulator.get_latency():.2f} ms")
        self.messages_label.setText(f"{self.simulator.get_message_count()}")
        self.rate_label.setText(f"{self.simulator.get_processing_rate():.1f} msgs/sec")
        
        # Update orderbook visualization
        self.update_orderbook_table()
    
    def update_orderbook_table(self):
        """Update the orderbook table with latest data"""
        orderbook = self.simulator.get_orderbook()
        if not orderbook:
            return
        
        # Get mid price for coloring
        mid_price = self.simulator.get_mid_price()
        
        # Clear table
        self.orderbook_table.clearContents()
        
        # Fill table with orderbook data
        max_rows = min(len(orderbook['bids']), len(orderbook['asks']), 20)
        
        for i in range(max_rows):
            # Bids (left column)
            if i < len(orderbook['bids']):
                bid_price, bid_size = orderbook['bids'][i]
                bid_item = QTableWidgetItem(f"{float(bid_size):.4f}")
                bid_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.orderbook_table.setItem(i, 0, bid_item)
                
                price_item = QTableWidgetItem(f"{float(bid_price):.2f}")
                price_item.setTextAlignment(Qt.AlignCenter)
                price_item.setBackground(QColor(200, 255, 200))  # Light green
                self.orderbook_table.setItem(i, 1, price_item)
            
            # Asks (right column)
            if i < len(orderbook['asks']):
                ask_price, ask_size = orderbook['asks'][i]
                ask_item = QTableWidgetItem(f"{float(ask_size):.4f}")
                ask_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.orderbook_table.setItem(i, 2, ask_item)
                
                if i == 0:  # Only set price for first ask to avoid duplicates
                    price_item = QTableWidgetItem(f"{float(ask_price):.2f}")
                    price_item.setTextAlignment(Qt.AlignCenter)
                    price_item.setBackground(QColor(255, 200, 200))  # Light red
                    self.orderbook_table.setItem(i, 1, price_item)