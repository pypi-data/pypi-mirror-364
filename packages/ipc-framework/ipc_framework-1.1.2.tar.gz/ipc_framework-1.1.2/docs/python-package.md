# IPC Framework - Python Package Documentation

[![PyPI version](https://badge.fury.io/py/ipc-framework.svg)](https://pypi.org/project/ipc-framework/)
[![Python versions](https://img.shields.io/pypi/pyversions/ipc-framework.svg)](https://pypi.org/project/ipc-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚨 **Critical Update - Version 1.1.0**

**IMPORTANT: Please upgrade immediately if using v1.0.0:**

```bash
pip install --upgrade ipc-framework
```

### 🛠️ **What's Fixed in v1.1.0:**
- ✅ **Added missing `create_response()` method** - Request/response pattern now functional
- ✅ **Fixed socket timeout deadlock** - Connections now stable after handshake
- ✅ **Fixed threading deadlock in receive operations** - No more hanging send/receive
- ✅ **Bidirectional communication working** - Python ↔ JavaScript fully operational

**Version 1.0.0 was largely broken due to these critical bugs. v1.1.0 provides a fully functional framework.**

## Table of Contents

- [Critical Update - Version 1.1.0](#critical-update---version-110)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [What's Working Now (v1.1.0)](#whats-working-now-v110)
- [Architecture Overview](#architecture-overview)
- [API Reference](#api-reference)
- [Core Classes](#core-classes)
- [Message Types](#message-types)
- [Examples](#examples)
- [Command Line Tools](#command-line-tools)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Installation

### Basic Installation

```bash
pip install ipc-framework
```

### With Optional Dependencies

```bash
# Install with example dependencies (psutil for monitoring)
pip install ipc-framework[examples]

# Install with development dependencies
pip install ipc-framework[dev]

# Install everything
pip install ipc-framework[all]
```

### Requirements

- Python 3.7+
- No external dependencies for core functionality

## What's Working Now (v1.1.0)

### ✅ **Request/Response Pattern - NOW WORKING**

```python
from ipc_framework import FrameworkServer, MessageType

# Server can now properly create responses
def handle_request(message):
    # This method was missing in v1.0.0, now works!
    response = message.create_response({
        'success': True,
        'data': {'timestamp': time.time()}
    })
    
    connection = server.connection_manager.get_connection(
        message.payload.get('connection_id')
    )
    server.send_to_connection(connection, response)
```

### ✅ **Client Communication - NOW WORKING**

```python
from ipc_framework import FrameworkClient

# Client connections now stable (no timeout deadlock)
client = FrameworkClient("my_app", host="localhost", port=8888)
client.connect()  # Now works without hanging!

# Send requests and receive responses (no threading deadlock)
response = client.send_request("api", {
    "action": "get_data",
    "connection_id": client.connection_id
})

print(f"Server response: {response.payload}")  # Now works!
```

### ✅ **Bidirectional Communication - NOW WORKING**

```python
# Python Server ↔ JavaScript Client communication
# Both directions working perfectly with v1.1.0 fixes
```

## Quick Start

### Server Setup

```python
from ipc_framework import FrameworkServer, MessageType
import time

# Create and configure server
server = FrameworkServer(host="localhost", port=8888)

# Create application
app = server.create_application("my_app", "My Application")

# Create channel
channel = app.create_channel("messages")

# Set up message handler
def handle_message(message):
    print(f"Received: {message.payload}")
    # Echo back to sender
    response = message.create_response({"echo": message.payload})
    connection = server.connection_manager.get_connection(
        message.payload.get('connection_id')
    )
    if connection:
        server.send_to_connection(connection, response)

channel.set_handler(MessageType.REQUEST, handle_message)

# Start server
server.start()
print("Server running on localhost:8888")

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    server.stop()
```

### Client Usage

```python
from ipc_framework import FrameworkClient
import time

# Create client
client = FrameworkClient("my_app", host="localhost", port=8888)

# Connect to server
if client.connect():
    print("Connected successfully!")
    
    # Send a message
    response = client.send_request("messages", {
        "text": "Hello, Server!",
        "connection_id": client.connection_id
    }, timeout=5.0)
    
    if response:
        print(f"Server responded: {response.payload}")
    
    client.disconnect()
else:
    print("Failed to connect")
```

## Architecture Overview

### Hierarchical Structure

```
IPC Server
├── Application 1 (app_id: "chat_app")
│   ├── Channel "general"
│   ├── Channel "tech_talk"
│   └── Channel "random"
├── Application 2 (app_id: "file_share")
│   ├── Channel "upload"
│   ├── Channel "download"
│   └── Channel "status"
└── Application 3 (app_id: "monitoring")
    ├── Channel "metrics"
    └── Channel "alerts"
```

### Message Flow

1. **Client connects** to server with an `app_id`
2. **Messages are routed** based on `app_id` → `channel_id`
3. **Handlers process** messages based on message type
4. **Responses/broadcasts** are sent back to relevant clients

## API Reference

### FrameworkServer

Main server class for handling IPC communications.

#### Constructor

```python
FrameworkServer(host="localhost", port=8888, max_connections=100)
```

**Parameters:**
- `host` (str): Server bind address (default: "localhost")
- `port` (int): Server port (default: 8888)
- `max_connections` (int): Maximum concurrent connections (default: 100)

#### Methods

##### `start()`
Start the IPC server.

```python
server.start()
```

##### `stop()`
Stop the IPC server gracefully.

```python
server.stop()
```

##### `create_application(app_id, name=None)`
Create a new application.

```python
app = server.create_application("my_app", "My Application")
```

**Parameters:**
- `app_id` (str): Unique application identifier
- `name` (str, optional): Human-readable application name

**Returns:** `Application` instance

##### `get_application(app_id)`
Get an existing application by ID.

```python
app = server.get_application("my_app")
```

##### `list_applications()`
Get information about all applications.

```python
apps = server.list_applications()
# Returns: Dict[str, Dict] with app info
```

##### `get_stats()`
Get server statistics.

```python
stats = server.get_stats()
# Returns: Dict with server statistics
```

### FrameworkClient

Client class for connecting to IPC server.

#### Constructor

```python
FrameworkClient(app_id, host="localhost", port=8888, connection_timeout=10.0)
```

**Parameters:**
- `app_id` (str): Application to connect to
- `host` (str): Server address (default: "localhost")
- `port` (int): Server port (default: 8888)
- `connection_timeout` (float): Connection timeout in seconds (default: 10.0)

#### Methods

##### `connect()`
Connect to the IPC server.

```python
success = client.connect()  # Returns: bool
```

##### `disconnect()`
Disconnect from the server.

```python
client.disconnect()
```

##### `send_message(channel_id, message_type, payload, reply_to=None)`
Send a message to a channel.

```python
message_id = client.send_message("my_channel", MessageType.REQUEST, {"data": "test"})
```

##### `send_request(channel_id, data, timeout=5.0)`
Send a request and wait for response.

```python
response = client.send_request("my_channel", {"query": "data"}, timeout=10.0)
```

##### `send_request_async(channel_id, data, callback)`
Send an async request with callback.

```python
def handle_response(response):
    print(f"Got response: {response.payload}")

client.send_request_async("my_channel", {"query": "data"}, handle_response)
```

##### `subscribe(channel_id, handler=None)`
Subscribe to a channel.

```python
def message_handler(message):
    print(f"Received: {message.payload}")

client.subscribe("notifications", message_handler)
```

##### `unsubscribe(channel_id)`
Unsubscribe from a channel.

```python
client.unsubscribe("notifications")
```

##### `publish(channel_id, data)`
Publish data to a channel.

```python
client.publish("announcements", {"text": "Server maintenance at 3 PM"})
```

##### `request(channel_id, data)`
Send a request message.

```python
message_id = client.request("api", {"endpoint": "users"})
```

##### `notify(channel_id, data)`
Send a notification message.

```python
client.notify("events", {"event": "user_login", "user_id": 123})
```

##### `ping(timeout=2.0)`
Ping the server to check connectivity.

```python
is_alive = client.ping()  # Returns: bool
```

## Core Classes

### Message

Represents a message in the IPC system.

#### Properties

```python
message.message_id      # str: Unique message identifier
message.app_id          # str: Application identifier
message.channel_id      # str: Channel identifier
message.message_type    # MessageType: Type of message
message.payload         # Any: Message data
message.timestamp       # float: Message timestamp
message.reply_to        # Optional[str]: For responses
```

#### Methods

```python
# Create response message
response = message.create_response({"result": "success"})

# Serialize to JSON
json_str = message.to_json()

# Deserialize from JSON
message = Message.from_json(json_str)

# Convert to dictionary
data = message.to_dict()
```

### Application

Represents an application with multiple channels.

#### Properties

```python
app.app_id           # str: Application identifier
app.name             # str: Application name
app.created_at       # float: Creation timestamp
app.last_activity    # float: Last activity timestamp
```

#### Methods

```python
# Create channel
channel = app.create_channel("my_channel")

# Get channel
channel = app.get_channel("my_channel")

# List channels
channels = app.list_channels()  # Returns: List[str]

# Remove channel
removed = app.remove_channel("my_channel")  # Returns: bool

# Update activity
app.update_activity()
```

### Channel

Represents a communication channel within an application.

#### Properties

```python
channel.channel_id    # str: Channel identifier
channel.app_id        # str: Parent application ID
channel.created_at    # float: Creation timestamp
```

#### Methods

```python
# Add subscriber
channel.add_subscriber("connection_123")

# Remove subscriber
channel.remove_subscriber("connection_123")

# Get subscribers
subscribers = channel.get_subscribers()  # Returns: List[str]

# Set message handler
channel.set_handler(MessageType.REQUEST, my_handler)

# Get handler
handler = channel.get_handler(MessageType.REQUEST)
```

## Message Types

### MessageType Enum

```python
from ipc_framework import MessageType

MessageType.REQUEST      # Request-response pattern
MessageType.RESPONSE     # Response to a request
MessageType.NOTIFICATION # One-way message
MessageType.SUBSCRIBE    # Subscribe to channel
MessageType.UNSUBSCRIBE  # Unsubscribe from channel
MessageType.PUBLISH      # Publish to subscribers
```

### Communication Patterns

#### 1. Request/Response Pattern

```python
# Client sends request
response = client.send_request("api", {"action": "get_users"})

# Server handles request and sends response
def handle_request(message):
    if message.payload.get("action") == "get_users":
        users = get_users_from_database()
        response = message.create_response({"users": users})
        server.send_to_connection(connection, response)
```

#### 2. Publish/Subscribe Pattern

```python
# Server publishes message
server.broadcast_to_application("chat_app", Message(
    app_id="chat_app",
    channel_id="general",
    message_type=MessageType.PUBLISH,
    payload={"text": "Welcome everyone!"}
))

# Client subscribes
def message_handler(message):
    print(f"Broadcast: {message.payload['text']}")

client.subscribe("general", message_handler)
```

#### 3. Notification Pattern

```python
# One-way notification (no response expected)
client.notify("events", {
    "event": "user_action",
    "user_id": 123,
    "action": "login"
})
```

## Examples

### Complete Chat Application

#### Server

```python
from ipc_framework import FrameworkServer, MessageType, Message
import time

class ChatServer:
    def __init__(self):
        self.server = FrameworkServer(host="localhost", port=8888)
        self.setup_chat_app()
    
    def setup_chat_app(self):
        # Create chat application
        app = self.server.create_application("chat_app", "Chat Application")
        
        # Create channels
        general = app.create_channel("general")
        tech_talk = app.create_channel("tech_talk")
        random = app.create_channel("random")
        
        # Set up handlers
        general.set_handler(MessageType.REQUEST, self.handle_chat_message)
        tech_talk.set_handler(MessageType.REQUEST, self.handle_chat_message)
        random.set_handler(MessageType.REQUEST, self.handle_chat_message)
    
    def handle_chat_message(self, message):
        username = message.payload.get('username', 'Anonymous')
        text = message.payload.get('text', '')
        
        print(f"[{message.channel_id}] {username}: {text}")
        
        # Broadcast to all subscribers
        broadcast_msg = Message(
            message_id="",
            app_id=message.app_id,
            channel_id=message.channel_id,
            message_type=MessageType.NOTIFICATION,
            payload={
                'type': 'chat_message',
                'username': username,
                'text': text,
                'timestamp': message.timestamp
            },
            timestamp=time.time()
        )
        
        app = self.server.get_application(message.app_id)
        channel = app.get_channel(message.channel_id)
        self.server._handle_publish(broadcast_msg, channel)
    
    def start(self):
        self.server.start()
        print("Chat server started on localhost:8888")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.server.stop()
            print("Chat server stopped")

if __name__ == "__main__":
    chat_server = ChatServer()
    chat_server.start()
```

#### Client

```python
from ipc_framework import FrameworkClient, MessageType
import threading
import time

class ChatClient:
    def __init__(self, username):
        self.username = username
        self.client = FrameworkClient("chat_app")
        self.current_channel = "general"
        self.running = False
    
    def connect(self):
        if self.client.connect():
            print(f"Connected as {self.username}")
            
            # Subscribe to channels
            self.client.subscribe("general", self.handle_message)
            self.client.subscribe("tech_talk", self.handle_message)
            self.client.subscribe("random", self.handle_message)
            
            return True
        return False
    
    def handle_message(self, message):
        if message.payload.get('type') == 'chat_message':
            username = message.payload.get('username')
            text = message.payload.get('text')
            
            if username != self.username:  # Don't show own messages
                print(f"\n[{message.channel_id}] {username}: {text}")
                print(f"[{self.current_channel}] {self.username}: ", end="", flush=True)
    
    def send_message(self, text):
        self.client.request(self.current_channel, {
            'username': self.username,
            'text': text,
            'connection_id': self.client.connection_id
        })
    
    def switch_channel(self, channel):
        if channel in ['general', 'tech_talk', 'random']:
            self.current_channel = channel
            print(f"Switched to #{channel}")
    
    def start_chat(self):
        self.running = True
        print(f"Welcome to chat! You're in #{self.current_channel}")
        print("Commands: /join <channel>, /quit")
        
        while self.running:
            try:
                user_input = input(f"[{self.current_channel}] {self.username}: ")
                
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    self.send_message(user_input)
            except KeyboardInterrupt:
                break
        
        self.client.disconnect()
    
    def handle_command(self, command):
        parts = command.split()
        
        if parts[0] == '/quit':
            self.running = False
        elif parts[0] == '/join' and len(parts) > 1:
            self.switch_channel(parts[1])

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python chat_client.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    client = ChatClient(username)
    
    if client.connect():
        client.start_chat()
    else:
        print("Failed to connect to server")
```

### File Sharing Application

```python
from ipc_framework import FrameworkServer, FrameworkClient, MessageType
import os
import time

class FileServer:
    def __init__(self):
        self.server = FrameworkServer()
        self.files = {}  # Simple in-memory file storage
        self.setup_file_app()
    
    def setup_file_app(self):
        app = self.server.create_application("file_share", "File Sharing")
        
        upload_channel = app.create_channel("upload")
        download_channel = app.create_channel("download")
        list_channel = app.create_channel("list")
        
        upload_channel.set_handler(MessageType.REQUEST, self.handle_upload)
        download_channel.set_handler(MessageType.REQUEST, self.handle_download)
        list_channel.set_handler(MessageType.REQUEST, self.handle_list)
    
    def handle_upload(self, message):
        filename = message.payload.get('filename')
        content = message.payload.get('content')
        
        if filename and content:
            self.files[filename] = {
                'content': content,
                'size': len(content),
                'uploaded_at': time.time()
            }
            
            response = message.create_response({
                'success': True,
                'message': f'File {filename} uploaded successfully'
            })
        else:
            response = message.create_response({
                'success': False,
                'message': 'Missing filename or content'
            })
        
        connection = self.server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        if connection:
            self.server.send_to_connection(connection, response)
    
    def handle_download(self, message):
        filename = message.payload.get('filename')
        
        if filename in self.files:
            response = message.create_response({
                'success': True,
                'filename': filename,
                'content': self.files[filename]['content']
            })
        else:
            response = message.create_response({
                'success': False,
                'message': f'File {filename} not found'
            })
        
        connection = self.server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        if connection:
            self.server.send_to_connection(connection, response)
    
    def handle_list(self, message):
        file_list = [
            {
                'filename': name,
                'size': info['size'],
                'uploaded_at': info['uploaded_at']
            }
            for name, info in self.files.items()
        ]
        
        response = message.create_response({
            'success': True,
            'files': file_list
        })
        
        connection = self.server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        if connection:
            self.server.send_to_connection(connection, response)

# Usage
server = FileServer()
server.server.start()
```

### Monitoring System

```python
from ipc_framework import FrameworkServer, MessageType, Message
import psutil
import time
import threading

class MonitoringServer:
    def __init__(self):
        self.server = FrameworkServer()
        self.setup_monitoring()
        self.monitoring_active = False
    
    def setup_monitoring(self):
        app = self.server.create_application("monitoring", "System Monitor")
        
        metrics_channel = app.create_channel("metrics")
        alerts_channel = app.create_channel("alerts")
        
        metrics_channel.set_handler(MessageType.NOTIFICATION, self.handle_metric)
        
        # Start system monitoring
        self.start_system_monitoring()
    
    def handle_metric(self, message):
        metric_name = message.payload.get('metric')
        value = message.payload.get('value', 0)
        
        print(f"Metric received: {metric_name} = {value}")
        
        # Generate alerts for high values
        if value > 80:
            alert = Message(
                message_id="",
                app_id="monitoring",
                channel_id="alerts",
                message_type=MessageType.PUBLISH,
                payload={
                    'type': 'high_usage_alert',
                    'metric': metric_name,
                    'value': value,
                    'severity': 'critical' if value > 95 else 'warning',
                    'timestamp': time.time()
                },
                timestamp=time.time()
            )
            
            app = self.server.get_application("monitoring")
            alerts_channel = app.get_channel("alerts")
            self.server._handle_publish(alert, alerts_channel)
    
    def start_system_monitoring(self):
        def monitor():
            while True:
                if self.monitoring_active:
                    # Get system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    # Send metrics
                    app = self.server.get_application("monitoring")
                    metrics_channel = app.get_channel("metrics")
                    
                    metrics = [
                        ("cpu_usage", cpu_percent),
                        ("memory_usage", memory.percent),
                        ("disk_usage", disk.percent)
                    ]
                    
                    for metric_name, value in metrics:
                        metric_msg = Message(
                            message_id="",
                            app_id="monitoring",
                            channel_id="metrics",
                            message_type=MessageType.NOTIFICATION,
                            payload={
                                'metric': metric_name,
                                'value': value,
                                'timestamp': time.time()
                            },
                            timestamp=time.time()
                        )
                        
                        self.handle_metric(metric_msg)
                
                time.sleep(5)  # Monitor every 5 seconds
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def enable_monitoring(self):
        self.monitoring_active = True
        print("System monitoring enabled")
    
    def disable_monitoring(self):
        self.monitoring_active = False
        print("System monitoring disabled")
```

## Command Line Tools

Your package includes several command-line tools:

### `ipc-server`
Start a demo server with multiple applications.

```bash
ipc-server
```

### `ipc-chat`
Start an interactive chat client.

```bash
ipc-chat your_username
```

### `ipc-file`
File sharing demo client.

```bash
# Interactive mode
ipc-file

# Simulation mode
ipc-file sim
```

### `ipc-monitor`
System monitoring client.

```bash
# Interactive mode
ipc-monitor

# Simulation mode
ipc-monitor sim
```

### `ipc-demo`
Run the full framework demonstration.

```bash
ipc-demo
```

## Advanced Usage

### Custom Connection Managers

```python
class CustomConnectionManager:
    def __init__(self):
        self.connections = {}
        self.connection_metadata = {}
    
    def add_connection(self, connection_id, connection_obj, app_id):
        self.connections[connection_id] = connection_obj
        self.connection_metadata[connection_id] = {
            'app_id': app_id,
            'connected_at': time.time(),
            'last_activity': time.time()
        }
    
    def update_activity(self, connection_id):
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]['last_activity'] = time.time()

# Use custom connection manager
server = FrameworkServer()
server.connection_manager = CustomConnectionManager()
```

### Message Middleware

```python
class MessageMiddleware:
    def __init__(self):
        self.middleware_stack = []
    
    def add_middleware(self, middleware_func):
        self.middleware_stack.append(middleware_func)
    
    def process_message(self, message):
        for middleware in self.middleware_stack:
            message = middleware(message)
            if message is None:  # Middleware can block messages
                return None
        return message

# Logging middleware
def logging_middleware(message):
    print(f"Processing message: {message.message_type} to {message.channel_id}")
    return message

# Authentication middleware
def auth_middleware(message):
    if not message.payload.get('auth_token'):
        print("Message blocked: Missing auth token")
        return None
    return message

# Use middleware
middleware = MessageMiddleware()
middleware.add_middleware(logging_middleware)
middleware.add_middleware(auth_middleware)
```

### Async Message Handling

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncHandler:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def handle_message_async(self, message):
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        # Process message
        result = await self.process_data(message.payload)
        
        # Send response
        response = message.create_response(result)
        return response
    
    async def process_data(self, data):
        # Simulate database operation
        await asyncio.sleep(0.5)
        return {"processed": True, "data": data}

# Use async handler
async_handler = AsyncHandler()

def sync_wrapper(message):
    # Run async handler in thread pool
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(
            async_handler.handle_message_async(message)
        )
        # Send response back to client
        # ... implementation depends on your server setup
    finally:
        loop.close()
```

### Load Balancing

```python
import random

class LoadBalancer:
    def __init__(self):
        self.servers = []
        self.current_index = 0
    
    def add_server(self, server):
        self.servers.append(server)
    
    def get_server_round_robin(self):
        if not self.servers:
            return None
        
        server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        return server
    
    def get_server_random(self):
        if not self.servers:
            return None
        return random.choice(self.servers)
    
    def get_server_least_connections(self):
        if not self.servers:
            return None
        
        return min(self.servers, 
                  key=lambda s: s.connection_manager.get_connection_count())

# Usage
load_balancer = LoadBalancer()
load_balancer.add_server(FrameworkServer(port=8888))
load_balancer.add_server(FrameworkServer(port=8889))
load_balancer.add_server(FrameworkServer(port=8890))

# Route to least loaded server
target_server = load_balancer.get_server_least_connections()
```

## Best Practices

### 1. Error Handling

```python
from ipc_framework.exceptions import IPCError, ConnectionError, RoutingError

try:
    client = FrameworkClient("my_app")
    client.connect()
    
    response = client.send_request("api", {"action": "test"})
    if response:
        print("Success:", response.payload)
    else:
        print("Request timed out")

except ConnectionError as e:
    print(f"Connection failed: {e}")
except RoutingError as e:
    print(f"Message routing failed: {e}")
except IPCError as e:
    print(f"IPC error: {e}")
finally:
    if client.connected:
        client.disconnect()
```

### 2. Resource Management

```python
from contextlib import contextmanager

@contextmanager
def ipc_client(app_id, **kwargs):
    client = FrameworkClient(app_id, **kwargs)
    try:
        if client.connect():
            yield client
        else:
            raise ConnectionError("Failed to connect")
    finally:
        if client.connected:
            client.disconnect()

# Usage
with ipc_client("my_app") as client:
    response = client.send_request("api", {"test": "data"})
    print(response.payload)
```

### 3. Configuration Management

```python
import os
from dataclasses import dataclass

@dataclass
class IPCConfig:
    host: str = "localhost"
    port: int = 8888
    max_connections: int = 100
    connection_timeout: float = 10.0
    
    @classmethod
    def from_env(cls):
        return cls(
            host=os.getenv("IPC_HOST", "localhost"),
            port=int(os.getenv("IPC_PORT", "8888")),
            max_connections=int(os.getenv("IPC_MAX_CONNECTIONS", "100")),
            connection_timeout=float(os.getenv("IPC_TIMEOUT", "10.0"))
        )

# Usage
config = IPCConfig.from_env()
server = FrameworkServer(
    host=config.host,
    port=config.port,
    max_connections=config.max_connections
)
```

### 4. Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('ipc_framework')

class LoggingServer(FrameworkServer):
    def route_message(self, message):
        logger.info(f"Routing message: {message.message_type} to {message.channel_id}")
        return super().route_message(message)

class LoggingClient(FrameworkClient):
    def send_message(self, channel_id, message_type, payload, reply_to=None):
        logger.info(f"Sending {message_type} to {channel_id}")
        return super().send_message(channel_id, message_type, payload, reply_to)
```

### 5. Testing

```python
import unittest
import time
import threading

class TestIPCFramework(unittest.TestCase):
    def setUp(self):
        self.server = FrameworkServer(port=9999)  # Use different port for testing
        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()
        time.sleep(0.1)  # Give server time to start
        
        # Set up test application
        app = self.server.create_application("test_app")
        channel = app.create_channel("test_channel")
        channel.set_handler(MessageType.REQUEST, self.echo_handler)
    
    def tearDown(self):
        if hasattr(self, 'client') and self.client.connected:
            self.client.disconnect()
        self.server.stop()
    
    def echo_handler(self, message):
        response = message.create_response({"echo": message.payload})
        connection = self.server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        if connection:
            self.server.send_to_connection(connection, response)
    
    def test_client_server_communication(self):
        self.client = FrameworkClient("test_app", port=9999)
        self.assertTrue(self.client.connect())
        
        response = self.client.send_request("test_channel", {
            "test": "data",
            "connection_id": self.client.connection_id
        })
        
        self.assertIsNotNone(response)
        self.assertEqual(response.payload["echo"]["test"], "data")
    
    def test_subscription(self):
        self.client = FrameworkClient("test_app", port=9999)
        self.assertTrue(self.client.connect())
        
        received_messages = []
        
        def message_handler(message):
            received_messages.append(message)
        
        self.client.subscribe("test_channel", message_handler)
        
        # Publish a message
        self.client.publish("test_channel", {"broadcast": "test"})
        
        time.sleep(0.1)  # Give time for message processing
        self.assertEqual(len(received_messages), 1)

if __name__ == "__main__":
    unittest.main()
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused

```python
# Problem: Server not running or wrong port
# Solution: Check server status and port configuration

try:
    client = FrameworkClient("my_app", port=8888)
    if not client.connect():
        print("Connection failed - check if server is running on port 8888")
except Exception as e:
    print(f"Connection error: {e}")
```

#### 2. Message Not Delivered

```python
# Problem: Channel doesn't exist or no subscribers
# Solution: Ensure channel exists and has subscribers

# Check if channel exists
app = server.get_application("my_app")
if app and app.get_channel("my_channel"):
    print("Channel exists")
else:
    print("Channel not found - create it first")
    app.create_channel("my_channel")
```

#### 3. Handler Not Called

```python
# Problem: Handler not set for message type
# Solution: Set appropriate handler

channel = app.get_channel("my_channel")
if not channel.get_handler(MessageType.REQUEST):
    print("No handler for REQUEST messages")
    channel.set_handler(MessageType.REQUEST, my_handler)
```

#### 4. Memory Leaks

```python
# Problem: Connections not properly cleaned up
# Solution: Always disconnect clients and stop servers

import atexit

def cleanup():
    if client.connected:
        client.disconnect()
    server.stop()

atexit.register(cleanup)
```

### Performance Optimization

#### 1. Connection Pooling

```python
class ConnectionPool:
    def __init__(self, app_id, size=10):
        self.app_id = app_id
        self.size = size
        self.pool = []
        self.used = set()
    
    def get_connection(self):
        if self.pool:
            conn = self.pool.pop()
            self.used.add(conn)
            return conn
        
        if len(self.used) < self.size:
            conn = FrameworkClient(self.app_id)
            if conn.connect():
                self.used.add(conn)
                return conn
        
        return None
    
    def return_connection(self, conn):
        if conn in self.used:
            self.used.remove(conn)
            self.pool.append(conn)
```

#### 2. Message Batching

```python
class MessageBatcher:
    def __init__(self, client, batch_size=10):
        self.client = client
        self.batch_size = batch_size
        self.batch = []
    
    def add_message(self, channel_id, data):
        self.batch.append((channel_id, data))
        
        if len(self.batch) >= self.batch_size:
            self.flush()
    
    def flush(self):
        if not self.batch:
            return
        
        # Send all messages in batch
        for channel_id, data in self.batch:
            self.client.notify(channel_id, data)
        
        self.batch.clear()
```

### Debugging

#### Enable Debug Logging

```python
import logging

# Enable debug logging for IPC framework
logging.getLogger('ipc_framework').setLevel(logging.DEBUG)

# Create console handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# Add handler to logger
logging.getLogger('ipc_framework').addHandler(handler)
```

#### Message Tracing

```python
class TracingClient(FrameworkClient):
    def _send_message(self, message):
        print(f"SEND: {message.to_dict()}")
        return super()._send_message(message)
    
    def handle_message(self, message):
        print(f"RECV: {message.to_dict()}")
        super().handle_message(message)
```

---

## License

This package is released under the MIT License. See LICENSE file for details.

## Support

- **PyPI Package**: https://pypi.org/project/ipc-framework/
- **Documentation**: https://github.com/ifesol/ipc-framework#readme
- **Issues**: https://github.com/ifesol/ipc-framework/issues 