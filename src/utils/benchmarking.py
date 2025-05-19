"""
Performance benchmarking utilities for the Trade Simulator
"""
import time
import logging
import threading
from typing import Dict, List, Callable, Any
import numpy as np

from src.config import BENCHMARK_INTERVAL_SEC

logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Utility for benchmarking performance metrics"""
    
    def __init__(self):
        """Initialize the performance benchmark"""
        self.metrics = {}
        self.running = False
        self.thread = None
        
        logger.info("Performance benchmark initialized")
    
    def start(self):
        """Start the benchmark monitoring"""
        if self.running:
            logger.warning("Benchmark already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Performance benchmark started")
    
    def stop(self):
        """Stop the benchmark monitoring"""
        if not self.running:
            logger.warning("Benchmark not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        logger.info("Performance benchmark stopped")
    
    def register_metric(self, name: str, callback: Callable[[], Any]):
        """Register a metric to be monitored"""
        self.metrics[name] = {
            "callback": callback,
            "values": [],
            "last_value": None,
            "min": None,
            "max": None,
            "avg": None,
            "p95": None,
            "p99": None
        }
        
        logger.info(f"Registered metric: {name}")
    
    def _monitor_loop(self):
        """Monitor loop for collecting metrics"""
        while self.running:
            self._collect_metrics()
            self._calculate_statistics()
            self._log_statistics()
            
            time.sleep(BENCHMARK_INTERVAL_SEC)
    
    def _collect_metrics(self):
        """Collect current values for all metrics"""
        for name, metric in self.metrics.items():
            try:
                value = metric["callback"]()
                metric["values"].append(value)
                metric["last_value"] = value
                
                # Keep only the last 1000 values
                if len(metric["values"]) > 1000:
                    metric["values"].pop(0)
            except Exception as e:
                logger.error(f"Error collecting metric {name}: {e}")
    
    def _calculate_statistics(self):
        """Calculate statistics for all metrics"""
        for name, metric in self.metrics.items():
            if not metric["values"]:
                continue
            
            values = np.array(metric["values"])
            
            metric["min"] = np.min(values)
            metric["max"] = np.max(values)
            metric["avg"] = np.mean(values)
            metric["p95"] = np.percentile(values, 95)
            metric["p99"] = np.percentile(values, 99)
    
    # def _  = np.percentile(values, 95)
    #         metric["p99"] = np.percentile(values, 99)
    
    def _log_statistics(self):
        """Log current statistics"""
        logger.info("Performance Benchmark Report:")
        
        for name, metric in self.metrics.items():
            if metric["last_value"] is None:
                continue
            
            logger.info(f"  {name}:")
            logger.info(f"    Current: {metric['last_value']}")
            logger.info(f"    Min: {metric['min']}")
            logger.info(f"    Max: {metric['max']}")
            logger.info(f"    Avg: {metric['avg']}")
            logger.info(f"    P95: {metric['p95']}")
            logger.info(f"    P99: {metric['p99']}")

class Timer:
    """Utility for timing code execution"""
    
    def __init__(self, name: str = None):
        """Initialize the timer"""
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """Start the timer"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """Stop the timer and log the result"""
        self.end_time = time.time()
        elapsed_ms = (self.end_time - self.start_time) * 1000
        
        if self.name:
            logger.debug(f"Timer '{self.name}': {elapsed_ms:.2f} ms")
        
        return elapsed_ms