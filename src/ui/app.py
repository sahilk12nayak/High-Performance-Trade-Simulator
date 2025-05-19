"""
Main application UI for the Trade Simulator
"""
import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QLabel, QStatusBar
from PyQt5.QtCore import Qt, QTimer

from src.ui.input_panel import InputPanel
from src.ui.output_panel import OutputPanel
from src.data.websocket_manager import WebSocketManager
from src.models.simulator import TradeSimulator
from src.config import UI_WINDOW_TITLE, UI_WINDOW_SIZE, UI_REFRESH_RATE_MS

logger = logging.getLogger(__name__)

class TradeSimulatorApp:
    """Main application class for the Trade Simulator"""
    
    def __init__(self):
        """Initialize the application"""
        self.app = QApplication(sys.argv)
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle(UI_WINDOW_TITLE)
        self.main_window.resize(*UI_WINDOW_SIZE)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create splitter for input and output panels
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # Create simulator and websocket manager
        self.simulator = TradeSimulator()
        self.websocket_manager = WebSocketManager(self.simulator)
        
        # Create input and output panels
        self.input_panel = InputPanel(self.simulator, self.websocket_manager)
        self.output_panel = OutputPanel(self.simulator)
        
        # Add panels to splitter
        self.splitter.addWidget(self.input_panel)
        self.splitter.addWidget(self.output_panel)
        self.splitter.setSizes([int(UI_WINDOW_SIZE[0] * 0.3), int(UI_WINDOW_SIZE[0] * 0.7)])
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.main_window.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Setup timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(UI_REFRESH_RATE_MS)
        
        logger.info("Application UI initialized")
    
    def update_ui(self):
        """Update the UI with latest data"""
        self.output_panel.update_display()
        
        # Update status bar with connection status
        if self.websocket_manager.is_connected():
            self.status_label.setText(f"Connected to {self.simulator.exchange} | Processing latency: {self.simulator.get_latency():.2f} ms")
        else:
            self.status_label.setText("Disconnected")
    
    def run(self):
        """Run the application"""
        self.main_window.show()
        return self.app.exec_()