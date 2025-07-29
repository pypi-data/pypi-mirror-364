# IPC Framework - Python Package

[![PyPI version](https://badge.fury.io/py/ipc-framework.svg)](https://pypi.org/project/ipc-framework/)
[![Python versions](https://img.shields.io/pypi/pyversions/ipc-framework.svg)](https://pypi.org/project/ipc-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Efficient Inter-Process Communication Framework** with hierarchical application and channel management. Enables seamless **bidirectional communication** between Python servers and JavaScript/TypeScript clients.

## 🚀 Key Features

- **🔄 Bidirectional Communication**: Full two-way messaging between Python ↔ JavaScript
- **🏗️ Hierarchical Organization**: Applications → Channels → Messages
- **📡 Multiple Patterns**: Request/Response, Pub/Sub, Notifications
- **🌍 Cross-Language**: Python server + JavaScript/TypeScript clients
- **⚡ High Performance**: WebSocket-based with optimized binary protocol
- **🛡️ Built-in Reliability**: Auto-reconnection, timeouts, error handling
- **📦 Zero Dependencies**: Pure Python implementation
- **🎯 Thread-Safe**: Safe for multi-threaded applications

## ✨ What's New in v1.1.0

🛠️ **Critical Bug Fixes**:
- ✅ **Fixed missing `create_response()` method** - Request/response now working
- ✅ **Fixed socket timeout deadlock** - Stable connections after handshake  
- ✅ **Fixed threading deadlock** - Resolved receive/send blocking issue
- ✅ **Fully functional bidirectional communication** - Both directions working perfectly

## 📦 Installation

```bash
pip install ipc-framework
```

## 🎯 Quick Start

### Python Server

```python
from ipc_framework import FrameworkServer, MessageType
import time

# Create server
server = FrameworkServer(host="localhost", port=8888)

# Create application and channel
app = server.create_application("my_app", "My Application")
api_channel = app.create_channel("api")

# Handle requests
def handle_request(message):
    if message.payload.get('action') == 'get_time':
        # Use the working create_response() method!
        response = message.create_response({
            'success': True,
            'time': time.time(),
            'message': 'Current server time'
        })
        
        connection = server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        server.send_to_connection(connection, response)

api_channel.set_handler(MessageType.REQUEST, handle_request)
server.start()
```

### Python Client

```python
from ipc_framework import FrameworkClient

# Create and connect client
client = FrameworkClient("my_app", host="localhost", port=8888)
client.connect()

# Send request and get response
response = client.send_request("api", {
    "action": "get_time",
    "connection_id": client.connection_id
})

print(f"Server time: {response.payload['time']}")
client.disconnect()
```

### JavaScript Client (Works with Python Server!)

```javascript
import { IPCClient } from '@ifesol/ipc-framework-js';

const client = new IPCClient('my_app', {
  host: 'localhost',
  port: 8888
});

await client.connect();

const response = await client.sendRequest('api', {
  action: 'get_time',
  connection_id: client.connectionId
});

console.log('Server time:', response.payload.time);
```

## 🔄 Communication Patterns

### 1. Request/Response (Bidirectional)
```python
# Client → Server → Client
response = client.send_request("api", {"action": "get_users"})
```

### 2. Pub/Sub Notifications (Server → Client)
```python
# Server broadcasts to all subscribers
def notification_handler(message):
    print(f"Notification: {message.payload}")

client.subscribe("notifications", notification_handler)
```

### 3. Real-time Updates (Both Directions)
```python
# Client can trigger server notifications
client.request("api", {"action": "trigger_notification"})
# Server sends real-time updates to all clients
```

## 🌍 Cross-Language Architecture

```
┌─────────────────┐    WebSocket     ┌──────────────────┐
│  Python Server  │ ←──────────────→ │ JavaScript Client│
│                 │                  │  (Browser/Node)  │
│  - Applications │                  │  - TypeScript    │
│  - Channels     │                  │  - React/Vue     │
│  - Message Routing                 │  - Auto-reconnect│
└─────────────────┘                  └──────────────────┘
```

## 📊 Performance & Reliability

| Feature | Status |
|---------|---------|
| **Bidirectional Messaging** | ✅ Working |
| **Connection Stability** | ✅ Fixed deadlocks |
| **Request/Response** | ✅ Working |
| **Pub/Sub** | ✅ Working |
| **Error Handling** | ✅ Built-in |
| **Thread Safety** | ✅ Fixed |
| **Auto-reconnection** | ✅ JS client |

## 🛠️ Command Line Tools

The package includes several CLI tools for testing:

```bash
# Start demo server
ipc-server

# Interactive chat client  
ipc-chat your_username

# File sharing demo
ipc-file

# System monitoring
ipc-monitor

# Full framework demo
ipc-demo
```

## 🎯 Use Cases

### Real-time Applications
- **Chat systems** with multiple channels
- **Live dashboards** with metric streaming  
- **Collaborative editors** with real-time updates
- **Gaming** with real-time state sync

### Web Applications  
- **Python backend** ↔ **React frontend**
- **API servers** with real-time notifications
- **Microservice communication**
- **IoT device control**

### Multi-Process Systems
- **Service-to-service** communication
- **Background task** coordination
- **Distributed processing**
- **Event-driven architectures**

## 📚 Documentation

- **[Complete Documentation](./docs/README.md)** - Full guides and examples
- **[API Reference](./docs/api-reference.md)** - Detailed API documentation  
- **[Integration Guide](./docs/integration-guide.md)** - Framework integration examples
- **[Examples](./docs/examples.md)** - Real-world usage examples

## 🆚 Why Choose IPC Framework?

| Traditional IPC | IPC Framework |
|----------------|---------------|
| ❌ Complex setup | ✅ 3-line setup |
| ❌ Python-only | ✅ Python ↔ JavaScript |
| ❌ Manual protocols | ✅ Built-in patterns |
| ❌ No web support | ✅ Direct browser clients |
| ❌ External dependencies | ✅ Zero dependencies |

## 🔗 Related Packages

- **JavaScript Client**: [@ifesol/ipc-framework-js](https://www.npmjs.com/package/@ifesol/ipc-framework-js)
- **NPM Package**: Full TypeScript support for Node.js and browsers

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Ready for production use!** 🚀 The framework now provides reliable, bidirectional communication between Python servers and JavaScript clients. 