# Getting Started - IPC Framework

**Node.js ↔ Python backend communication made simple!**

This guide will get you up and running with **`@ifesol/ipc-framework-nodejs`** v1.1.0 in under 5 minutes.

## 📦 **Installation**

### **Step 1: Install Node.js Package**
```bash
npm install @ifesol/ipc-framework-nodejs
```

### **Step 2: Install Python Server**
```bash
pip install --upgrade ipc-framework  # v1.1.0+ required for Node.js compatibility
```

## 🚀 **Quick Start**

### **Python Server (server.py)**

```python
from ipc_framework import FrameworkServer, MessageType
import time

# Create server
server = FrameworkServer(host="localhost", port=8888)

# Create application and channel
app = server.create_application("my_app", "My Application")
api_channel = app.create_channel("api")

# Handle requests from Node.js
def handle_request(message):
    action = message.payload.get('action')
    
    if action == 'get_data':
        # Using v1.1.0 working create_response() method
        response = message.create_response({
            'success': True,
            'data': {'timestamp': time.time(), 'message': 'Hello from Python!'},
            'server': 'Python v1.1.0'
        })
        
        connection = server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        server.send_to_connection(connection, response)

api_channel.set_handler(MessageType.REQUEST, handle_request)

print("🐍 Python IPC Server starting on localhost:8888")
server.start()
```

### **Node.js Client (client.js)**

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

async function main() {
    console.log('🟢 Node.js IPC Client starting...');

    // Create client
    const client = new IPCClient('my_app', {
        host: 'localhost',
        port: 8888
    });

    try {
        // Connect to Python server
        await client.connect();
        console.log('✅ Connected to Python server!');

        // Send request and get response
        const response = await client.sendRequest('api', {
            action: 'get_data',
            connection_id: client.connectionId
        });

        console.log('📨 Response from Python:', response.payload);

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        client.disconnect();
    }
}

main();
```

### **Run the Example**

```bash
# Terminal 1: Start Python server
python server.py

# Terminal 2: Run Node.js client
node client.js
```

**Expected Output:**
```
🐍 Python IPC Server starting on localhost:8888
🟢 Node.js IPC Client starting...
✅ Connected to Python server!
📨 Response from Python: {
  success: true,
  data: { timestamp: 1234567890, message: 'Hello from Python!' },
  server: 'Python v1.1.0'
}
```

## 🔄 **Communication Patterns**

### **1. Request/Response**

```javascript
// Node.js → Python → Node.js
const response = await client.sendRequest('processing', {
    action: 'process_data',
    data: { user_id: 123, items: [1, 2, 3] },
    connection_id: client.connectionId
});

console.log('Processed:', response.payload.result);
```

### **2. Real-time Notifications**

```javascript
// Subscribe to Python notifications
client.subscribe('alerts', (message) => {
    console.log('🚨 Alert from Python:', message.payload);
});

// Python can send real-time updates to Node.js
```

### **3. Multiple Channels**

```javascript
// Connect to different services
const dataResponse = await client.sendRequest('data_service', { action: 'get_users' });
const mlResponse = await client.sendRequest('ml_models', { action: 'predict', features: [] });
const analyticsResponse = await client.sendRequest('analytics', { action: 'get_metrics' });
```

## 🏗️ **Express.js Integration**

```javascript
const express = require('express');
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

const app = express();
const pythonClient = new IPCClient('web_api');

app.use(express.json());

// Initialize IPC connection
pythonClient.connect().then(() => {
    console.log('🔗 Connected to Python backend');
});

// API endpoint using Python backend
app.post('/api/process', async (req, res) => {
    try {
        const result = await pythonClient.sendRequest('processing', {
            action: 'process_user_data',
            data: req.body,
            connection_id: pythonClient.connectionId
        });
        
        res.json(result.payload);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('🌐 Express server running on port 3000');
});
```

## 🎯 **Use Cases**

### **Web APIs with Python Backend**
- **Express.js** frontend serving APIs
- **Python** backend for data processing, ML models, analytics

### **Microservice Architecture**
- **Node.js** services for web/API handling
- **Python** services for data science, ML, heavy computation

### **Real-time Applications**
- **Node.js** handling real-time web connections
- **Python** providing real-time analytics, alerts, notifications

### **Hybrid Applications**
- **Node.js** for rapid web development
- **Python** for data analysis, machine learning, scientific computing

## 📊 **Performance Benefits**

| Feature | HTTP REST | IPC Framework |
|---------|-----------|---------------|
| **Latency** | 5-50ms | <1ms |
| **Overhead** | HTTP headers | Minimal binary |
| **Connections** | Per request | Persistent |
| **Real-time** | Polling/WebSocket | Built-in pub/sub |
| **Type Safety** | Manual | TypeScript definitions |

## 🔧 **Configuration Options**

```javascript
const client = new IPCClient('my_app', {
    host: 'localhost',              // Python server host
    port: 8888,                     // Python server port  
    connectionTimeout: 10000,       // Connection timeout (ms)
    reconnectAttempts: 5,           // Auto-reconnect attempts
    reconnectDelay: 2000           // Delay between reconnects (ms)
});
```

## 🛠️ **Error Handling**

```javascript
try {
    const response = await client.sendRequest('api', data, 5000); // 5s timeout
    console.log('Success:', response.payload);
    
} catch (error) {
    if (error.message.includes('timeout')) {
        console.log('Request timed out - Python server may be busy');
    } else if (error.message.includes('connection')) {
        console.log('Connection lost - check Python server');
    } else {
        console.log('Other error:', error.message);
    }
}
```

## 🚨 **Troubleshooting**

### **"Connection failed"**
- ✅ Ensure Python server is running: `python server.py`
- ✅ Check port is available: `netstat -an | findstr 8888`
- ✅ Verify Python package version: `pip show ipc-framework` (should be v1.1.0+)

### **"Request timeout"**
- ✅ Python server may be processing - increase timeout
- ✅ Check Python server logs for errors
- ✅ Verify the channel exists and has handlers

### **"No response"**
- ✅ Ensure Python handler calls `message.create_response()` (v1.1.0 fix)
- ✅ Verify `connection_id` is passed in requests
- ✅ Check Python server is sending response back

## 📚 **Next Steps**

- **[Complete API Reference](./api-reference.md)** - Full documentation
- **[Production Examples](./examples.md)** - Real-world usage patterns
- **[Integration Guide](./integration-guide.md)** - Framework integration
- **[Python Server Docs](./python-package.md)** - Python server setup

## 🔗 **Resources**

- **NPM Package**: https://www.npmjs.com/package/@ifesol/ipc-framework-nodejs
- **Python Package**: https://pypi.org/project/ipc-framework/
- **GitHub**: https://github.com/ifesol/ipc-framework-nodejs

---

**Ready to build amazing Node.js ↔ Python applications!** 🚀 