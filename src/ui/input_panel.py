"""
Input panel for the Trade Simulator
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QGroupBox, QHBoxLayout, QRadioButton
)
from PyQt5.QtCore import Qt

from src.config import EXCHANGES, DEFAULT_EXCHANGE, DEFAULT_PAIR, DEFAULT_ORDER_TYPE, DEFAULT_QUANTITY, DEFAULT_VOLATILITY, DEFAULT_FEE_TIER

logger = logging.getLogger(__name__)

class InputPanel(QWidget):
    """Input panel widget for simulation parameters"""
    
    def __init__(self, simulator, websocket_manager):
        """Initialize the input panel"""
        super().__init__()
        self.simulator = simulator
        self.websocket_manager = websocket_manager
        
        self.init_ui()
        logger.info("Input panel initialized")
    
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Input Parameters")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Form layout for parameters
        form_group = QGroupBox("Simulation Parameters")
        form_layout = QFormLayout()
        
        # Exchange selection
        self.exchange_combo = QComboBox()
        for exchange in EXCHANGES:
            self.exchange_combo.addItem(exchange)
        self.exchange_combo.setCurrentText(DEFAULT_EXCHANGE)
        self.exchange_combo.currentTextChanged.connect(self.on_exchange_changed)
        form_layout.addRow("Exchange:", self.exchange_combo)
        
        # Pair selection
        self.pair_combo = QComboBox()
        self.update_pairs()
        self.pair_combo.currentTextChanged.connect(self.on_pair_changed)
        form_layout.addRow("Spot Asset:", self.pair_combo)
        
        # Order type
        self.order_type_layout = QHBoxLayout()
        self.market_radio = QRadioButton("Market")
        self.market_radio.setChecked(True)
        self.limit_radio = QRadioButton("Limit")
        self.limit_radio.setEnabled(False)  # Disabled as per requirements
        self.order_type_layout.addWidget(self.market_radio)
        self.order_type_layout.addWidget(self.limit_radio)
        form_layout.addRow("Order Type:", self.order_type_layout)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(1, 10000)
        self.quantity_spin.setValue(DEFAULT_QUANTITY)
        self.quantity_spin.setSuffix(" USD")
        self.quantity_spin.valueChanged.connect(self.on_parameter_changed)
        form_layout.addRow("Quantity:", self.quantity_spin)
        
        # Volatility
        self.volatility_spin = QDoubleSpinBox()
        self.volatility_spin.setRange(0.001, 1.0)
        self.volatility_spin.setValue(DEFAULT_VOLATILITY)
        self.volatility_spin.setSingleStep(0.001)
        self.volatility_spin.setDecimals(3)
        self.volatility_spin.valueChanged.connect(self.on_parameter_changed)
        form_layout.addRow("Volatility:", self.volatility_spin)
        
        # Fee tier
        self.fee_tier_combo = QComboBox()
        self.update_fee_tiers()
        self.fee_tier_combo.currentTextChanged.connect(self.on_parameter_changed)
        form_layout.addRow("Fee Tier:", self.fee_tier_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Connection controls
        conn_group = QGroupBox("Connection")
        conn_layout = QVBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_button)
        
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setAlignment(Qt.AlignCenter)
        conn_layout.addWidget(self.connection_status)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        # Apply initial parameters to simulator
        self.apply_parameters()
    
    def update_pairs(self):
        """Update the available pairs based on selected exchange"""
        exchange = self.exchange_combo.currentText()
        self.pair_combo.clear()
        for pair in EXCHANGES[exchange].available_pairs:
            self.pair_combo.addItem(pair)
    
    def update_fee_tiers(self):
        """Update the available fee tiers based on selected exchange"""
        exchange = self.exchange_combo.currentText()
        self.fee_tier_combo.clear()
        for tier in EXCHANGES[exchange].fee_tiers:
            self.fee_tier_combo.addItem(tier)
    
    def on_exchange_changed(self):
        """Handle exchange selection change"""
        self.update_pairs()
        self.update_fee_tiers()
        self.apply_parameters()
    
    def on_pair_changed(self):
        """Handle pair selection change"""
        self.apply_parameters()
        
        # If connected, reconnect to new websocket
        if self.websocket_manager.is_connected():
            self.websocket_manager.disconnect()
            self.websocket_manager.connect()
    
    def on_parameter_changed(self):
        """Handle parameter changes"""
        self.apply_parameters()
    
    def apply_parameters(self):
        """Apply current parameters to the simulator"""
        exchange = self.exchange_combo.currentText()
        pair = self.pair_combo.currentText()
        order_type = "market" if self.market_radio.isChecked() else "limit"
        quantity = self.quantity_spin.value()
        volatility = self.volatility_spin.value()
        fee_tier = self.fee_tier_combo.currentText()
        
        self.simulator.set_parameters(
            exchange=exchange,
            pair=pair,
            order_type=order_type,
            quantity=quantity,
            volatility=volatility,
            fee_tier=fee_tier
        )
        
        logger.debug(f"Applied parameters: {exchange}, {pair}, {order_type}, {quantity}, {volatility}, {fee_tier}")
    
    def toggle_connection(self):
        """Toggle WebSocket connection"""
        if self.websocket_manager.is_connected():
            self.websocket_manager.disconnect()
            self.connect_button.setText("Connect")
            self.connection_status.setText("Disconnected")
        else:
            self.websocket_manager.connect()
            self.connect_button.setText("Disconnect")
            self.connection_status.setText(f"Connected to {self.simulator.exchange}")