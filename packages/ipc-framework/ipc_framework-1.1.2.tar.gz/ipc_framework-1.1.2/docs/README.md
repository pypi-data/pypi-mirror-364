# IPC Framework Documentation

Comprehensive documentation for **Node.js ↔ Python** backend IPC communication.

## 📦 Published Packages

### Python Server Package
- **PyPI**: [ipc-framework](https://pypi.org/project/ipc-framework/)
- **Version**: 1.1.0 ⭐ **LATEST - Critical Bug Fixes**
- **Install**: `pip install --upgrade ipc-framework`

### Node.js Client Package  
- **NPM**: [@ifesol/ipc-framework-nodejs](https://www.npmjs.com/package/@ifesol/ipc-framework-nodejs)
- **Version**: 1.1.0 ⭐ **PUBLISHED - Ready for Production**
- **Install**: `npm install @ifesol/ipc-framework-nodejs`

## 🚨 **Important: Version 1.1.0 Critical Updates**

**If you're using Python IPC Framework, please upgrade to v1.1.0 immediately:**

```bash
pip install --upgrade ipc-framework
```

### 🛠️ **Critical Bug Fixes in v1.1.0:**
- ✅ **Fixed missing `create_response()` method** - Request/response pattern now working
- ✅ **Fixed socket timeout deadlock** - Stable connections after handshake  
- ✅ **Fixed threading deadlock** - Resolved receive/send blocking issue
- ✅ **Fully functional bidirectional communication** - Python ↔ JavaScript working perfectly

**Version 1.0.0 had critical bugs that made the package largely non-functional. All users should upgrade to v1.1.0.**

## 📚 Documentation Structure

### 🚀 Getting Started
- **[Getting Started Guide](./getting-started.md)** - 5-minute quick start with published packages
- **[Installation Guide](./installation-guide.md)** - Complete installation for Node.js and Python packages
- **[Quick Start Examples](./examples.md#basic-setup)** - Get up and running in minutes

### 📖 API Documentation
- **[Python Server API](./python-package.md)** - Complete Python server documentation
- **[Node.js Client API](./nodejs-package.md)** - Complete Node.js client documentation
- **[API Reference](./api-reference.md)** - Unified API reference for both packages

### 💡 Examples & Tutorials
- **[Complete Examples](./examples.md)** - Real-world usage examples
  - Express.js + Python Backend
  - Microservice Architecture (Node.js + Python)
  - Real-time Analytics Dashboard
  - Data Processing Pipelines
  - ML Model Integration

## 🏗️ Architecture Overview

### Hierarchical Structure
```
Python IPC Server (TCP:8888)
├── Application 1 (app_id: "web_api")
│   ├── Channel "users"
│   ├── Channel "orders" 
│   └── Channel "analytics"
├── Application 2 (app_id: "data_service")
│   ├── Channel "processing"
│   └── Channel "ml_models"
└── Application 3 (app_id: "notifications")
    ├── Channel "real_time"
    └── Channel "alerts"

Node.js Clients (TCP connections)
├── Express.js API Server → "web_api"
├── Data Collector Service → "data_service"  
└── Dashboard Service → "notifications"
```

### Communication Flow
1. **JavaScript Client** connects to **Python Server** with an `app_id`
2. **Messages** are routed based on `app_id` → `channel_id`
3. **Handlers** process messages based on message type
4. **Responses/broadcasts** are sent back to relevant clients

## 🔄 Communication Patterns

### 1. Request/Response
```python
# Python Server
def handle_request(message):
    result = process_data(message.payload)
    response = message.create_response(result)
    server.send_to_connection(connection, response)
```

```typescript
// JavaScript Client
const response = await client.sendRequest('api', { action: 'get_users' });
console.log(response?.payload);
```

### 2. Publish/Subscribe
```python
# Python Server - Broadcast to all subscribers
server._handle_publish(message, channel)
```

```typescript
// JavaScript Client
client.subscribe('notifications', (message) => {
  console.log('Notification:', message.payload);
});

client.publish('announcements', { title: 'System Update' });
```

### 3. Notifications
```typescript
// JavaScript Client - One-way message
client.notify('events', {
  type: 'user_action',
  userId: 'user123',
  action: 'login'
});
```

## 🌟 Key Features

### Python Package (Server)
- 🚀 **WebSocket-based** high-performance server
- 🏗️ **Hierarchical structure** with apps and channels
- 🔄 **Multiple communication patterns** (request/response, pub/sub, notifications)
- 📊 **Built-in monitoring** and statistics
- 🛠️ **Command-line tools** for testing and demos
- 🐍 **Python 3.7+** support with type hints

### JavaScript Package (Client)
- 🌐 **Universal client** (Node.js + Browser)
- 📘 **TypeScript-first** with full type safety
- 🔄 **Auto-reconnection** with exponential backoff
- 💓 **Heartbeat mechanism** for connection health
- 📦 **Multiple builds** (CommonJS, ESM, UMD)
- ⚛️ **React-ready** with modern bundler support

## 🚀 Quick Example

### Python Server
```python
from ipc_framework import FrameworkServer, MessageType

server = FrameworkServer(host="localhost", port=8888)
app = server.create_application("my_app")
channel = app.create_channel("messages")

def handle_message(message):
    print(f"Received: {message.payload}")
    response = message.create_response({"echo": message.payload})
    connection = server.connection_manager.get_connection(
        message.payload.get('connection_id')
    )
    server.send_to_connection(connection, response)

channel.set_handler(MessageType.REQUEST, handle_message)
server.start()
```

### JavaScript Client
```typescript
import { IPCClient } from '@ifesol/ipc-framework-js';

const client = new IPCClient('my_app');
await client.connect();

const response = await client.sendRequest('messages', {
  text: 'Hello from JavaScript!',
  connection_id: client.connectionId
});

console.log('Server response:', response?.payload);
client.disconnect();
```

## 🔧 Installation

### Python
```bash
pip install ipc-framework
```

### JavaScript/TypeScript
```bash
# Node.js
npm install @ifesol/ipc-framework-js ws

# Browser (via CDN)
# <script src="https://unpkg.com/@ifesol/ipc-framework-js@1.0.0/dist/browser/index.js"></script>
```

## 🌍 Use Cases

### Real-time Applications
- **Chat systems** with multiple channels
- **Collaborative editors** with live updates
- **Gaming** with real-time state synchronization
- **Live dashboards** with metric streaming

### API Integration
- **REST-like APIs** with real-time updates
- **Microservice communication** between Python and JavaScript services
- **Event-driven architectures** with pub/sub messaging
- **File transfer systems** with progress tracking

### Multi-platform Communication
- **Python backend** ↔ **React frontend**
- **Python services** ↔ **Node.js services**
- **Desktop apps** ↔ **Web apps**
- **Mobile apps** ↔ **Server applications**

## 📋 Message Types

| Type | Description | Pattern |
|------|-------------|---------|
| `REQUEST` | Send request, expect response | Client → Server → Client |
| `RESPONSE` | Response to a request | Auto-generated |
| `NOTIFICATION` | One-way message | Client → Server |
| `SUBSCRIBE` | Subscribe to channel | Client → Server |
| `UNSUBSCRIBE` | Unsubscribe from channel | Client → Server |
| `PUBLISH` | Broadcast to subscribers | Server → All Subscribers |

## 🛠️ Command Line Tools

The Python package includes several CLI tools:

```bash
# Start demo server with multiple applications
ipc-server

# Interactive chat client
ipc-chat your_username

# File sharing demo
ipc-file

# System monitoring demo
ipc-monitor

# Complete framework demonstration
ipc-demo
```

## 🔗 Integration Examples

### React Hook
```typescript
const useIPCClient = (appId: string) => {
  const [client] = useState(() => new IPCClient(appId));
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {
    client.onConnected(() => setConnected(true));
    client.onDisconnected(() => setConnected(false));
    client.connect();
    return () => client.disconnect();
  }, []);
  
  return { client, connected };
};
```

### Vue.js Composable
```typescript
export function useIPC(appId: string) {
  const client = ref<IPCClient>();
  const connected = ref(false);
  
  onMounted(async () => {
    client.value = new IPCClient(appId);
    await client.value.connect();
  });
  
  return { client, connected };
}
```

### Angular Service
```typescript
@Injectable({ providedIn: 'root' })
export class IPCService {
  private client = new IPCClient('angular_app');
  
  async connect() {
    return await this.client.connect();
  }
  
  subscribeToChannel(channelId: string): Observable<Message> {
    return new Observable(observer => {
      this.client.subscribe(channelId, observer.next);
    });
  }
}
```

## 🎯 Best Practices

### Error Handling
```typescript
try {
  const response = await client.sendRequest('api', data, 5000);
  if (!response) throw new Error('Request timeout');
} catch (error) {
  console.error('Request failed:', error.message);
}
```

### Resource Management
```typescript
// Always cleanup connections
const client = new IPCClient('my_app');
try {
  await client.connect();
  // Use client...
} finally {
  client.disconnect();
}
```

### Connection Monitoring
```typescript
client.onConnected(() => console.log('✅ Connected'));
client.onDisconnected(() => console.log('❌ Disconnected'));
client.onError((error) => console.error('🚨 Error:', error));
```

## 📈 Performance Tips

### Python Server
- Use connection pooling for high-load scenarios
- Implement message batching for frequent updates
- Consider `uvloop` for better async performance

### JavaScript Client
- Use connection pooling in Node.js applications
- Implement debouncing for frequent messages
- Use ES modules for better tree-shaking

## 🆘 Support & Community

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and examples
- **Examples**: Real-world usage scenarios
- **Type Safety**: Full TypeScript support

## 📄 License

Both packages are released under the MIT License.

---

## 🚀 Ready to Get Started?

1. **[Install the packages](./installation-guide.md)**
2. **[Try the basic example](./examples.md#basic-setup)**
3. **[Explore the full API](./api-reference.md)**
4. **[Build your first real-time app](./examples.md#chat-application)**

Happy coding! 🎉 