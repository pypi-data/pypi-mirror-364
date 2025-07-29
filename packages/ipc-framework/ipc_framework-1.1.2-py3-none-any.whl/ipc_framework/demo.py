#!/usr/bin/env python3
"""
IPC Framework Demo

This script demonstrates all the key features of the IPC framework:
- Multiple applications and channels
- Different message types (request/response, publish/subscribe, notifications)
- Connection management
- Error handling

Run this script to see the framework in action!
"""

import time
import threading
import random
from . import FrameworkServer, FrameworkClient, MessageType, Message


def run_demo():
    print("🚀 IPC Framework Demo")
    print("=" * 50)
    
    # Step 1: Create and start server
    print("\n📡 Starting IPC Server...")
    server = FrameworkServer(host="localhost", port=8888)
    
    # Create multiple applications
    chat_app = server.create_application("chat_app", "Chat Application")
    file_app = server.create_application("file_share", "File Sharing")
    monitor_app = server.create_application("monitoring", "System Monitor")
    
    # Create channels in each application
    chat_app.create_channel("general")
    chat_app.create_channel("announcements")
    
    file_app.create_channel("upload")
    file_app.create_channel("download")
    
    monitor_app.create_channel("metrics")
    monitor_app.create_channel("alerts")
    
    # Set up message handlers
    def chat_handler(message: Message):
        username = message.payload.get('username', 'Anonymous')
        text = message.payload.get('text', '')
        print(f"💬 [Chat] {username}: {text}")
    
    def file_handler(message: Message):
        action = message.payload.get('action', 'unknown')
        filename = message.payload.get('filename', 'unknown')
        print(f"📁 [File] {action}: {filename}")
    
    def metric_handler(message: Message):
        metric = message.payload.get('metric', 'unknown')
        value = message.payload.get('value', 0)
        print(f"📊 [Metrics] {metric}: {value}%")
        
        # Generate alert if CPU high
        if metric == 'cpu_usage' and value > 80:
            alert_msg = Message(
                message_id="",
                app_id="monitoring",
                channel_id="alerts",
                message_type=MessageType.NOTIFICATION,
                payload={
                    'type': 'high_cpu_alert',
                    'metric': metric,
                    'value': value,
                    'severity': 'warning'
                },
                timestamp=time.time()
            )
            server._handle_publish(alert_msg, monitor_app.get_channel("alerts"))
    
    # Set handlers
    chat_app.get_channel("general").set_handler(MessageType.REQUEST, chat_handler)
    file_app.get_channel("upload").set_handler(MessageType.REQUEST, file_handler)
    monitor_app.get_channel("metrics").set_handler(MessageType.NOTIFICATION, metric_handler)
    
    # Start server
    server.start()
    print("✅ Server started successfully!")
    
    # Show server status
    print(f"\n📋 Server Configuration:")
    for app_id, app_info in server.list_applications().items():
        print(f"  📱 {app_id} ({app_info['name']})")
        for channel in app_info['channels']:
            print(f"    📺 {channel}")
    
    time.sleep(1)
    
    # Step 2: Create clients and demonstrate features
    print("\n👥 Creating Clients...")
    
    clients = []
    
    # Chat clients
    alice = FrameworkClient("chat_app", host="localhost", port=8888)
    bob = FrameworkClient("chat_app", host="localhost", port=8888)
    
    # File client
    file_client = FrameworkClient("file_share", host="localhost", port=8888)
    
    # Monitoring client
    monitor_client = FrameworkClient("monitoring", host="localhost", port=8888)
    
    # Connect all clients
    for name, client in [("Alice", alice), ("Bob", bob), ("FileClient", file_client), ("Monitor", monitor_client)]:
        if client.connect():
            clients.append((name, client))
            print(f"✅ {name} connected")
        else:
            print(f"❌ {name} failed to connect")
    
    time.sleep(1)
    
    # Step 3: Demonstrate different message patterns
    print("\n🎭 Demonstrating Message Patterns...")
    
    # 1. Chat messages (Request pattern)
    print("\n💬 Chat Messages:")
    alice.request("general", {"username": "Alice", "text": "Hello everyone!"})
    time.sleep(0.5)
    bob.request("general", {"username": "Bob", "text": "Hi Alice! How are you?"})
    time.sleep(0.5)
    alice.request("general", {"username": "Alice", "text": "I'm great! This IPC framework is awesome!"})
    time.sleep(1)
    
    # 2. File operations
    print("\n📁 File Operations:")
    file_client.request("upload", {"action": "upload", "filename": "document.pdf", "size": 1024000})
    time.sleep(0.5)
    file_client.request("upload", {"action": "upload", "filename": "image.jpg", "size": 2048000})
    time.sleep(1)
    
    # 3. Monitoring with alerts
    print("\n📊 System Monitoring:")
    
    # Subscribe to alerts
    def alert_handler(message: Message):
        alert_type = message.payload.get('type', 'unknown')
        metric = message.payload.get('metric', 'unknown')
        value = message.payload.get('value', 0)
        print(f"🚨 ALERT: {alert_type} - {metric} at {value}%")
    
    monitor_client.subscribe("alerts", alert_handler)
    time.sleep(0.5)  # Give subscription time to register
    
    # Send normal metrics
    monitor_client.notify("metrics", {"metric": "cpu_usage", "value": 45})
    time.sleep(0.5)
    monitor_client.notify("metrics", {"metric": "memory_usage", "value": 62})
    time.sleep(0.5)
    
    # Send high CPU to trigger alert
    monitor_client.notify("metrics", {"metric": "cpu_usage", "value": 85})
    time.sleep(1)
    
    # 4. Publish/Subscribe pattern
    print("\n📢 Publish/Subscribe Demo:")
    
    # Subscribe to announcements
    def announcement_handler(message: Message):
        text = message.payload.get('text', '')
        print(f"📢 ANNOUNCEMENT: {text}")
    
    alice.subscribe("announcements", announcement_handler)
    bob.subscribe("announcements", announcement_handler)
    time.sleep(0.5)
    
    # Publish announcement
    alice.publish("announcements", {"text": "Server maintenance scheduled for tonight at 11 PM"})
    time.sleep(1)
    
    # Step 4: Show server statistics
    print("\n📈 Server Statistics:")
    stats = server.get_stats()
    print(f"  🔗 Active connections: {stats['total_connections']}")
    print(f"  📱 Applications: {stats['total_applications']}")
    
    for app_id, app_info in server.list_applications().items():
        channels_info = server.list_channels(app_id)
        print(f"  📱 {app_id}: {app_info['connections']} connections")
        for channel_id, channel_info in channels_info.items():
            print(f"    📺 {channel_id}: {channel_info['subscribers']} subscribers")
    
    # Step 5: Demonstrate connection management
    print("\n🔌 Connection Management Demo:")
    print("Disconnecting some clients...")
    
    alice.disconnect()
    print("❌ Alice disconnected")
    time.sleep(0.5)
    
    file_client.disconnect()
    print("❌ FileClient disconnected")
    time.sleep(1)
    
    # Show updated stats
    stats = server.get_stats()
    print(f"📊 Updated connections: {stats['total_connections']}")
    
    # Step 6: Error handling demo
    print("\n⚠️  Error Handling Demo:")
    
    # Try to send message with disconnected client
    try:
        alice.request("general", {"text": "This should fail"})
    except Exception as e:
        print(f"🚫 Expected error from disconnected client: {type(e).__name__}")
    
    # Try invalid channel
    try:
        bob.request("nonexistent_channel", {"text": "This will work but route to nowhere"})
        print("📝 Message sent to auto-created channel (framework auto-creates channels)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    time.sleep(1)
    
    # Step 7: Cleanup
    print("\n🧹 Cleaning up...")
    
    # Disconnect remaining clients
    for name, client in clients:
        if client.connected:
            client.disconnect()
            print(f"❌ {name} disconnected")
    
    # Stop server
    server.stop()
    print("🛑 Server stopped")
    
    print("\n🎉 Demo completed!")
    print("\n💡 Key Features Demonstrated:")
    print("  ✅ Multiple applications with channels (app_id -> channel_id)")
    print("  ✅ Request/Response pattern")
    print("  ✅ Publish/Subscribe pattern") 
    print("  ✅ Notifications and alerts")
    print("  ✅ Connection management")
    print("  ✅ Automatic channel creation")
    print("  ✅ Thread-safe operations")
    print("  ✅ Error handling")
    print("  ✅ Server statistics and monitoring")
    
    print("\n🚀 Try running the example scripts next:")
    print("  ipc-server         # Start the server")
    print("  ipc-chat YourName  # Chat client")
    print("  ipc-file           # File sharing client")
    print("  ipc-monitor sim    # Monitoring simulation")


def main():
    """Entry point for the demo command"""
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 