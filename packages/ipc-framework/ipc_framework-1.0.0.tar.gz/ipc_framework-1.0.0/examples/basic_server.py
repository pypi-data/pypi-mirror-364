#!/usr/bin/env python3
"""
Basic IPC Server Example

This example demonstrates how to create an IPC server with multiple applications
and channels, showing the hierarchical structure of app_id -> channel_id.
"""

import time
import threading
from ipc_framework import FrameworkServer, MessageType, Message


def setup_chat_application(server: FrameworkServer):
    """Setup a chat application with multiple channels"""
    app = server.create_application("chat_app", "Chat Application")
    
    # Create channels
    general_channel = app.create_channel("general")
    tech_channel = app.create_channel("tech_talk")
    random_channel = app.create_channel("random")
    
    # Set up message handlers
    def handle_chat_message(message: Message):
        print(f"[{message.channel_id}] Chat message from {message.payload.get('username', 'Anonymous')}: {message.payload.get('text', '')}")
        
        # Broadcast to all subscribers in this channel
        broadcast_msg = Message(
            message_id="",
            app_id=message.app_id,
            channel_id=message.channel_id,
            message_type=MessageType.NOTIFICATION,
            payload={
                'type': 'chat_message',
                'username': message.payload.get('username', 'Anonymous'),
                'text': message.payload.get('text', ''),
                'timestamp': message.timestamp
            },
            timestamp=time.time()
        )
        server._handle_publish(broadcast_msg, app.get_channel(message.channel_id))
    
    def handle_user_join(message: Message):
        username = message.payload.get('username', 'Anonymous')
        print(f"[{message.channel_id}] User {username} joined")
        
        # Notify other users
        join_msg = Message(
            message_id="",
            app_id=message.app_id,
            channel_id=message.channel_id,
            message_type=MessageType.NOTIFICATION,
            payload={
                'type': 'user_joined',
                'username': username,
                'timestamp': time.time()
            },
            timestamp=time.time()
        )
        server._handle_publish(join_msg, app.get_channel(message.channel_id))
    
    # Set handlers for all channels
    for channel_id in ["general", "tech_talk", "random"]:
        channel = app.get_channel(channel_id)
        channel.set_handler(MessageType.REQUEST, handle_chat_message)
        channel.set_handler(MessageType.NOTIFICATION, handle_user_join)


def setup_file_sharing_application(server: FrameworkServer):
    """Setup a file sharing application"""
    app = server.create_application("file_share", "File Sharing Service")
    
    # Create channels for different file operations
    upload_channel = app.create_channel("upload")
    download_channel = app.create_channel("download")
    status_channel = app.create_channel("status")
    
    def handle_file_upload(message: Message):
        filename = message.payload.get('filename', 'unknown')
        size = message.payload.get('size', 0)
        print(f"[file_share:upload] File upload request: {filename} ({size} bytes)")
        
        # Simulate file processing
        status_msg = Message(
            message_id="",
            app_id=message.app_id,
            channel_id="status",
            message_type=MessageType.NOTIFICATION,
            payload={
                'type': 'upload_progress',
                'filename': filename,
                'progress': 100,
                'status': 'completed'
            },
            timestamp=time.time()
        )
        server._handle_publish(status_msg, app.get_channel("status"))
    
    def handle_file_download(message: Message):
        filename = message.payload.get('filename', 'unknown')
        print(f"[file_share:download] File download request: {filename}")
        
        # Send response back to requester
        response = Message(
            message_id="",
            app_id=message.app_id,
            channel_id=message.channel_id,
            message_type=MessageType.RESPONSE,
            payload={
                'filename': filename,
                'download_url': f"http://example.com/files/{filename}",
                'expires_at': time.time() + 3600  # 1 hour
            },
            timestamp=time.time(),
            reply_to=message.message_id
        )
        
        # Find the connection that sent the request and send response
        connection_id = message.payload.get('connection_id')
        if connection_id:
            connection = server.connection_manager.get_connection(connection_id)
            if connection:
                server.send_to_connection(connection, response)
    
    upload_channel.set_handler(MessageType.REQUEST, handle_file_upload)
    download_channel.set_handler(MessageType.REQUEST, handle_file_download)


def setup_monitoring_application(server: FrameworkServer):
    """Setup a monitoring application"""
    app = server.create_application("monitoring", "System Monitoring")
    
    metrics_channel = app.create_channel("metrics")
    alerts_channel = app.create_channel("alerts")
    
    def handle_metric_report(message: Message):
        metric_name = message.payload.get('metric', 'unknown')
        value = message.payload.get('value', 0)
        print(f"[monitoring:metrics] Metric {metric_name}: {value}")
        
        # Check for alerts
        if metric_name == "cpu_usage" and value > 80:
            alert_msg = Message(
                message_id="",
                app_id=message.app_id,
                channel_id="alerts",
                message_type=MessageType.NOTIFICATION,
                payload={
                    'type': 'high_cpu_alert',
                    'metric': metric_name,
                    'value': value,
                    'threshold': 80,
                    'severity': 'warning'
                },
                timestamp=time.time()
            )
            server._handle_publish(alert_msg, app.get_channel("alerts"))
    
    metrics_channel.set_handler(MessageType.NOTIFICATION, handle_metric_report)


def main():
    # Create and configure the server
    server = FrameworkServer(host="localhost", port=8888)
    
    print("Setting up IPC Framework Server...")
    
    # Setup different applications
    setup_chat_application(server)
    setup_file_sharing_application(server)
    setup_monitoring_application(server)
    
    print("Applications configured:")
    for app_id, app_info in server.list_applications().items():
        print(f"  - {app_id} ({app_info['name']}): {len(app_info['channels'])} channels")
        for channel in app_info['channels']:
            print(f"    * {channel}")
    
    # Start the server
    server.start()
    
    try:
        print("\nServer is running. Press Ctrl+C to stop.")
        print("You can now run client examples to interact with the server.")
        print("\nServer Statistics:")
        
        while True:
            time.sleep(10)
            stats = server.get_stats()
            apps = server.list_applications()
            
            print(f"\n--- Server Stats ---")
            print(f"Active connections: {stats['total_connections']}")
            print(f"Active applications: {stats['total_applications']}")
            
            for app_id, app_info in apps.items():
                channels_info = server.list_channels(app_id)
                print(f"  {app_id}: {app_info['connections']} connections")
                for channel_id, channel_info in channels_info.items():
                    print(f"    {channel_id}: {channel_info['subscribers']} subscribers")
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()
        print("Server stopped.")


if __name__ == "__main__":
    main() 