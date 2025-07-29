#!/usr/bin/env python3
"""
Monitoring Client Example

This example demonstrates how to use the IPC framework for system monitoring.
It shows metrics reporting and alert subscription patterns.
"""

import time
import random
import threading
from .. import FrameworkClient, Message, MessageType

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class MonitoringClient:
    def __init__(self, client_name: str, host: str = "localhost", port: int = 8888):
        self.client_name = client_name
        self.client = FrameworkClient("monitoring", host, port)
        self.running = False
        self.metrics_thread = None
    
    def connect(self):
        """Connect to the monitoring server"""
        if self.client.connect():
            print(f"Monitoring client '{self.client_name}' connected")
            
            # Subscribe to alerts
            self.client.subscribe("alerts", self.handle_alert)
            return True
        else:
            print("Failed to connect to server")
            return False
    
    def handle_alert(self, message: Message):
        """Handle system alerts"""
        payload = message.payload
        alert_type = payload.get('type', 'unknown')
        
        if alert_type == 'high_cpu_alert':
            metric = payload.get('metric', 'unknown')
            value = payload.get('value', 0)
            threshold = payload.get('threshold', 0)
            severity = payload.get('severity', 'info')
            
            print(f"\n🚨 ALERT [{severity.upper()}]: {alert_type}")
            print(f"   Metric: {metric}")
            print(f"   Current: {value}%")
            print(f"   Threshold: {threshold}%")
            print(f"   Time: {time.strftime('%H:%M:%S')}")
    
    def send_metric(self, metric_name: str, value: float):
        """Send a metric to the monitoring system"""
        self.client.notify("metrics", {
            'metric': metric_name,
            'value': value,
            'client': self.client_name,
            'timestamp': time.time()
        })
    
    def get_system_metrics(self) -> dict:
        """Get current system metrics"""
        if HAS_PSUTIL:
            try:
                return {
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'load_average': psutil.getloadavg()[0] * 100,  # 1-minute load average as percentage
                }
            except Exception:
                pass
        
        # Fallback with simulated metrics if psutil not available or fails
        return {
            'cpu_usage': random.uniform(10, 95),
            'memory_usage': random.uniform(30, 80),
            'disk_usage': random.uniform(40, 70),
            'load_average': random.uniform(5, 50),
        }
    
    def start_monitoring(self, interval: float = 5.0):
        """Start continuous monitoring"""
        self.running = True
        
        def monitor_loop():
            while self.running:
                try:
                    metrics = self.get_system_metrics()
                    
                    for metric_name, value in metrics.items():
                        self.send_metric(metric_name, value)
                        print(f"[{self.client_name}] {metric_name}: {value:.1f}%")
                    
                    print(f"[{self.client_name}] Metrics sent at {time.strftime('%H:%M:%S')}")
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    time.sleep(interval)
        
        self.metrics_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.metrics_thread.start()
        print(f"Started monitoring with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.metrics_thread and self.metrics_thread.is_alive():
            self.metrics_thread.join(timeout=1.0)
        print("Monitoring stopped")
    
    def send_custom_metric(self, name: str, value: float):
        """Send a custom metric"""
        self.send_metric(name, value)
        print(f"Custom metric sent: {name} = {value}")
    
    def disconnect(self):
        """Disconnect from the server"""
        self.stop_monitoring()
        self.client.disconnect()
        print(f"Monitoring client '{self.client_name}' disconnected")


def simulate_monitoring():
    """Simulate multiple monitoring clients"""
    clients = []
    
    # Create monitoring clients for different "servers"
    server_names = ["web-server-1", "db-server", "api-gateway"]
    
    for server_name in server_names:
        client = MonitoringClient(server_name)
        if client.connect():
            clients.append(client)
            # Start monitoring with different intervals
            client.start_monitoring(interval=random.uniform(3, 7))
        time.sleep(0.5)
    
    if not clients:
        print("No monitoring clients could connect")
        return
    
    print(f"\n=== Started monitoring {len(clients)} systems ===")
    print("Monitoring will run for 30 seconds...")
    print("Watch for alerts when CPU usage exceeds 80%")
    
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopping simulation...")
    
    # Stop all monitoring
    for client in clients:
        client.disconnect()
    
    print("\n=== Monitoring simulation completed ===")


def interactive_mode():
    """Run in interactive mode"""
    client_name = input("Enter monitoring client name: ").strip() or "MonitoringClient"
    client = MonitoringClient(client_name)
    
    if not client.connect():
        return
    
    print("\n=== Monitoring Client ===")
    print("Commands:")
    print("  start [interval]     - Start automatic monitoring (default 5s)")
    print("  stop                 - Stop automatic monitoring")
    print("  metric <name> <val>  - Send custom metric")
    print("  status               - Show current system metrics")
    print("  quit                 - Exit")
    
    auto_monitoring = False
    
    try:
        while True:
            if not auto_monitoring:
                command = input(f"\n[{client_name}] > ").strip().split()
            else:
                # In auto monitoring mode, just wait for input with timeout
                print(f"\n[{client_name}] (auto-monitoring) > ", end="", flush=True)
                command = input().strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'start':
                if not auto_monitoring:
                    interval = 5.0
                    if len(command) > 1:
                        try:
                            interval = float(command[1])
                        except ValueError:
                            print("Invalid interval, using 5 seconds")
                    client.start_monitoring(interval)
                    auto_monitoring = True
                else:
                    print("Monitoring is already running. Use 'stop' first.")
            elif cmd == 'stop':
                if auto_monitoring:
                    client.stop_monitoring()
                    auto_monitoring = False
                else:
                    print("Monitoring is not running")
            elif cmd == 'metric' and len(command) >= 3:
                try:
                    name = command[1]
                    value = float(command[2])
                    client.send_custom_metric(name, value)
                except ValueError:
                    print("Invalid metric value")
            elif cmd == 'status':
                metrics = client.get_system_metrics()
                print("Current system metrics:")
                for name, value in metrics.items():
                    print(f"  {name}: {value:.1f}%")
            else:
                print("Invalid command or missing arguments")
    
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


def main():
    import sys
    
    print("System Monitoring Client")
    print("This example requires 'psutil' for real system metrics.")
    print("If not available, simulated metrics will be used.\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'sim':
        simulate_monitoring()
    else:
        interactive_mode()


if __name__ == "__main__":
    main() 