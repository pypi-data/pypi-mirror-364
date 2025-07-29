# IPC Framework - Node.js Package Documentation

[![npm version](https://badge.fury.io/js/%40ifesol%2Fipc-framework-nodejs.svg)](https://www.npmjs.com/package/@ifesol/ipc-framework-nodejs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎉 **FIXED v1.1.1** - Node.js ↔ Python TCP Communication

**✅ The NPM package is now working correctly!** This documentation reflects the **fixed v1.1.1** implementation.

**⚠️ Previous versions (1.1.0 and earlier) were broken** - make sure to use v1.1.1+

## 🔗 **Python Server Integration Required**

**This Node.js package requires a Python IPC server. Install the working Python package:**
```bash
pip install --upgrade ipc-framework  # Must be v1.1.0+
```

**Python v1.1.0+ required for reliable Node.js ↔ Python communication. v1.0.0 has critical bugs.**

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [TCP Connection](#tcp-connection)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Express.js Integration](#expressjs-integration)
- [Microservices Architecture](#microservices-architecture)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Migration from v1.1.0](#migration-from-v110)
- [Troubleshooting](#troubleshooting)

## Installation

### Node.js Package (FIXED!)

```bash
# Install the WORKING Node.js IPC client
npm install @ifesol/ipc-framework-nodejs@latest
```

### Python Server (Required)

```bash
# Install the Python IPC server
pip install --upgrade ipc-framework  # v1.1.0+ required
```

## Quick Start

### Basic Node.js Client

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

async function main() {
    // Create client with TCP connection
    const client = new IPCClient('my_app', {
        host: 'localhost',
        port: 8888,
        reconnectAttempts: 5,
        reconnectDelay: 2000
    });

    // Set up event handlers
    client.onConnected(() => {
        console.log('✅ Connected to Python server via TCP');
    });

    client.onDisconnected(() => {
        console.log('📡 Disconnected from Python server');
    });

    client.onError((error) => {
        console.error('❌ Connection error:', error.message);
    });

    try {
        // Connect to Python server
        const connected = await client.connect();
        if (!connected) {
            throw new Error('Failed to connect to Python server');
        }

        // Subscribe to real-time notifications
        client.subscribe('notifications', (message) => {
            console.log('🔔 Notification:', message.payload);
        });

        // Send request and get response
        const response = await client.sendRequest('api', {
            action: 'get_users',
            filters: { active: true }
        });

        console.log('📥 API Response:', response.payload);

        // Publish data to subscribers
        client.publish('events', {
            type: 'user_action',
            action: 'data_requested',
            timestamp: Date.now()
        });

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        client.disconnect();
    }
}

main().catch(console.error);
```

## TCP Connection

### Connection Architecture

The Node.js package uses **TCP sockets** (not WebSockets) to communicate with Python IPC servers:

```javascript
// TCP connection with proper message framing
const client = new IPCClient('my_app', {
    host: 'localhost',      // Python server host
    port: 8888,             // Python server port
    connectionTimeout: 10000, // Connection timeout (ms)
    reconnectAttempts: 5,   // Auto-reconnection attempts
    reconnectDelay: 2000,   // Delay between reconnection attempts (ms)
    heartbeatInterval: 30000 // Heartbeat interval (ms)
});
```

### Message Protocol

Messages use 4-byte length headers for reliable TCP framing:

```
┌─────────────┬─────────────────────────────────┐
│   Length    │         JSON Message            │
│  (4 bytes)  │        (variable length)        │
└─────────────┴─────────────────────────────────┘
```

### Connection Health

```javascript
// Check connection health
const isHealthy = await client.healthCheck();
console.log('Server healthy:', isHealthy);

// Get connection information
const info = client.getConnectionInfo();
console.log('Connection info:', info);
```

## API Reference

### IPCClient Class

#### Constructor

```javascript
const client = new IPCClient(appId, options);
```

**Parameters:**
- `appId` (string): Unique application identifier
- `options` (object): Configuration options
  - `host` (string, default: 'localhost'): Server host
  - `port` (number, default: 8888): Server port
  - `connectionTimeout` (number, default: 10000): Connection timeout in ms
  - `reconnectAttempts` (number, default: 5): Number of reconnection attempts
  - `reconnectDelay` (number, default: 2000): Delay between reconnection attempts in ms
  - `heartbeatInterval` (number, default: 30000): Heartbeat interval in ms

#### Methods

##### connect()
```javascript
const connected = await client.connect();
```
Establishes TCP connection to Python server. Returns `true` if successful.

##### disconnect()
```javascript
client.disconnect();
```
Closes the connection and cleans up resources.

##### sendRequest(channelId, payload, timeout)
```javascript
const response = await client.sendRequest('api', {
    action: 'get_data',
    params: { id: 123 }
}, 10000);
```
Sends a request and waits for response. Returns response message.

##### subscribe(channelId, handler)
```javascript
client.subscribe('notifications', (message) => {
    console.log('Received:', message.payload);
});
```
Subscribes to a channel for real-time notifications.

##### unsubscribe(channelId)
```javascript
client.unsubscribe('notifications');
```
Unsubscribes from a channel.

##### publish(channelId, data)
```javascript
client.publish('events', {
    type: 'user_action',
    timestamp: Date.now()
});
```
Publishes data to a channel.

##### healthCheck()
```javascript
const isHealthy = await client.healthCheck();
```
Checks if the connection to the server is healthy.

##### getConnectionInfo()
```javascript
const info = client.getConnectionInfo();
```
Returns connection information including ID, status, and subscribed channels.

#### Event Handlers

##### onConnected(handler)
```javascript
client.onConnected(() => {
    console.log('Connected to server');
});
```

##### onDisconnected(handler)
```javascript
client.onDisconnected(() => {
    console.log('Disconnected from server');
});
```

##### onError(handler)
```javascript
client.onError((error) => {
    console.error('Connection error:', error);
});
```

## Examples

### Basic Usage

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

async function basicExample() {
    const client = new IPCClient('basic-app');
    
    await client.connect();
    
    // Send ping
    const pingResponse = await client.sendRequest('system', { action: 'ping' });
    console.log('Ping response:', pingResponse.payload);
    
    // Get server time
    const timeResponse = await client.sendRequest('system', { action: 'get_time' });
    console.log('Server time:', timeResponse.payload);
    
    client.disconnect();
}

basicExample();
```

### Real-time Notifications

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

async function notificationExample() {
    const client = new IPCClient('notification-app');
    
    await client.connect();
    
    // Subscribe to status updates
    client.subscribe('status', (message) => {
        console.log('Status update:', message.payload);
    });
    
    // Subscribe to alerts
    client.subscribe('alerts', (message) => {
        console.log('Alert received:', message.payload);
    });
    
    // Keep running to receive notifications
    console.log('Listening for notifications... Press Ctrl+C to exit');
    
    process.on('SIGINT', () => {
        client.disconnect();
        process.exit(0);
    });
}

notificationExample();
```

### Data Processing Pipeline

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class DataProcessor {
    constructor() {
        this.client = new IPCClient('data-processor', {
            reconnectAttempts: 10,
            reconnectDelay: 3000
        });
    }
    
    async start() {
        await this.client.connect();
        
        // Subscribe to incoming data
        this.client.subscribe('raw_data', this.processData.bind(this));
        
        console.log('Data processor started');
    }
    
    async processData(message) {
        const { data, id } = message.payload;
        
        try {
            // Send data to Python for processing
            const result = await this.client.sendRequest('processor', {
                action: 'process_data',
                data: data,
                options: {
                    algorithm: 'advanced',
                    validate: true
                }
            });
            
            // Publish processed result
            this.client.publish('processed_data', {
                id: id,
                result: result.payload,
                processed_at: Date.now()
            });
            
        } catch (error) {
            console.error(`Failed to process data ${id}:`, error.message);
            
            // Publish error notification
            this.client.publish('errors', {
                id: id,
                error: error.message,
                timestamp: Date.now()
            });
        }
    }
}

const processor = new DataProcessor();
processor.start();
```

## Express.js Integration

### Basic Integration

```javascript
const express = require('express');
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

const app = express();
app.use(express.json());

// Initialize IPC client
const ipcClient = new IPCClient('express-api-server', {
    host: 'localhost',
    port: 8888,
    reconnectAttempts: 5
});

// Connect to Python server on startup
async function initializeIPC() {
    const connected = await ipcClient.connect();
    if (!connected) {
        console.error('Failed to connect to Python server');
        process.exit(1);
    }
    console.log('✅ Connected to Python IPC server');
}

// Middleware to attach IPC client to requests
app.use((req, res, next) => {
    req.ipc = ipcClient;
    next();
});

// API endpoints
app.get('/api/users', async (req, res) => {
    try {
        const response = await req.ipc.sendRequest('user_service', {
            action: 'get_all_users',
            filters: req.query
        });
        
        res.json({
            success: true,
            users: response.payload
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.post('/api/users', async (req, res) => {
    try {
        const response = await req.ipc.sendRequest('user_service', {
            action: 'create_user',
            user_data: req.body
        });
        
        res.json({
            success: true,
            user: response.payload
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Real-time events using Server-Sent Events
app.get('/api/events', (req, res) => {
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    });
    
    // Subscribe to notifications
    req.ipc.subscribe('notifications', (message) => {
        res.write(`data: ${JSON.stringify(message.payload)}\n\n`);
    });
    
    // Send initial connection message
    res.write(`data: ${JSON.stringify({ type: 'connected', timestamp: Date.now() })}\n\n`);
    
    // Clean up on disconnect
    req.on('close', () => {
        req.ipc.unsubscribe('notifications');
    });
});

// Health check endpoint
app.get('/health', async (req, res) => {
    try {
        const isHealthy = await ipcClient.healthCheck();
        res.json({
            status: isHealthy ? 'healthy' : 'unhealthy',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            message: error.message
        });
    }
});

// Start server
const PORT = process.env.PORT || 3000;

async function startServer() {
    await initializeIPC();
    
    app.listen(PORT, () => {
        console.log(`🚀 Express server running on port ${PORT}`);
        console.log(`📡 IPC connection established`);
    });
}

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Shutting down...');
    ipcClient.disconnect();
    process.exit(0);
});

startServer();
```

### Advanced Express Integration

```javascript
const express = require('express');
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class IPCExpressService {
    constructor() {
        this.app = express();
        this.client = null;
        this.isReady = false;
        
        this.setupMiddleware();
        this.setupRoutes();
    }
    
    async initialize() {
        // Initialize IPC client
        this.client = new IPCClient('express-service', {
            host: process.env.IPC_HOST || 'localhost',
            port: parseInt(process.env.IPC_PORT) || 8888,
            reconnectAttempts: 10,
            reconnectDelay: 3000
        });
        
        // Set up connection handlers
        this.client.onConnected(() => {
            console.log('✅ IPC client connected');
            this.isReady = true;
        });
        
        this.client.onDisconnected(() => {
            console.log('⚠️ IPC client disconnected');
            this.isReady = false;
        });
        
        this.client.onError((error) => {
            console.error('❌ IPC client error:', error.message);
        });
        
        // Connect
        const connected = await this.client.connect();
        if (!connected) {
            throw new Error('Failed to connect to IPC server');
        }
        
        return this;
    }
    
    setupMiddleware() {
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));
        
        // Add IPC client to request context
        this.app.use((req, res, next) => {
            req.ipc = this.client;
            req.ipcReady = this.isReady;
            next();
        });
        
        // Health check middleware
        this.app.use('/api/*', (req, res, next) => {
            if (!this.isReady) {
                return res.status(503).json({
                    error: 'IPC service unavailable',
                    message: 'Connection to Python server is not ready'
                });
            }
            next();
        });
    }
    
    setupRoutes() {
        // Generic API proxy
        this.app.all('/api/:service/:action', async (req, res) => {
            try {
                const { service, action } = req.params;
                const payload = {
                    action: action,
                    data: req.body,
                    query: req.query,
                    method: req.method
                };
                
                const response = await req.ipc.sendRequest(service, payload, 30000);
                
                res.json({
                    success: true,
                    result: response.payload
                });
                
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });
        
        // Real-time events
        this.app.get('/events/:channel', (req, res) => {
            const { channel } = req.params;
            
            res.writeHead(200, {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            });
            
            req.ipc.subscribe(channel, (message) => {
                res.write(`data: ${JSON.stringify(message.payload)}\n\n`);
            });
            
            req.on('close', () => {
                req.ipc.unsubscribe(channel);
            });
        });
        
        // System status
        this.app.get('/status', async (req, res) => {
            try {
                const connectionInfo = this.client?.getConnectionInfo();
                const isHealthy = await this.client?.healthCheck();
                
                res.json({
                    status: 'ok',
                    ipc: {
                        connected: this.isReady,
                        healthy: isHealthy,
                        connection: connectionInfo
                    },
                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                res.status(500).json({
                    status: 'error',
                    error: error.message
                });
            }
        });
    }
    
    async start(port = 3000) {
        await this.initialize();
        
        return new Promise((resolve) => {
            this.server = this.app.listen(port, () => {
                console.log(`🚀 IPC Express Service running on port ${port}`);
                resolve(this);
            });
        });
    }
    
    async stop() {
        if (this.client) {
            this.client.disconnect();
        }
        
        if (this.server) {
            this.server.close();
        }
    }
}

// Usage
const service = new IPCExpressService();
service.start(3000);

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('Shutting down...');
    await service.stop();
    process.exit(0);
});
```

## Microservices Architecture

### Service Discovery Pattern

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class MicroserviceClient {
    constructor(serviceName, options = {}) {
        this.serviceName = serviceName;
        this.client = new IPCClient(`${serviceName}-client`, {
            host: options.host || process.env.IPC_HOST || 'localhost',
            port: options.port || process.env.IPC_PORT || 8888,
            ...options
        });
        
        this.services = new Map();
        this.isReady = false;
    }
    
    async initialize() {
        await this.client.connect();
        
        // Subscribe to service discovery updates
        this.client.subscribe('service_discovery', (message) => {
            this.handleServiceUpdate(message.payload);
        });
        
        // Request current service list
        const response = await this.client.sendRequest('system', {
            action: 'list_services'
        });
        
        if (response.payload.services) {
            response.payload.services.forEach(service => {
                this.services.set(service.name, service);
            });
        }
        
        this.isReady = true;
        console.log(`✅ ${this.serviceName} initialized with ${this.services.size} available services`);
    }
    
    handleServiceUpdate(update) {
        const { action, service } = update;
        
        switch (action) {
            case 'service_registered':
                this.services.set(service.name, service);
                console.log(`📝 Service registered: ${service.name}`);
                break;
                
            case 'service_unregistered':
                this.services.delete(service.name);
                console.log(`📝 Service unregistered: ${service.name}`);
                break;
                
            case 'service_health_changed':
                if (this.services.has(service.name)) {
                    this.services.get(service.name).healthy = service.healthy;
                }
                break;
        }
    }
    
    async callService(serviceName, action, data = {}, options = {}) {
        if (!this.isReady) {
            throw new Error('Microservice client not initialized');
        }
        
        const service = this.services.get(serviceName);
        if (!service) {
            throw new Error(`Service not found: ${serviceName}`);
        }
        
        if (!service.healthy) {
            throw new Error(`Service unhealthy: ${serviceName}`);
        }
        
        return await this.client.sendRequest(serviceName, {
            action: action,
            data: data,
            source_service: this.serviceName,
            ...options
        });
    }
    
    async broadcastEvent(eventType, data) {
        this.client.publish('events', {
            type: eventType,
            data: data,
            source: this.serviceName,
            timestamp: Date.now()
        });
    }
    
    subscribeToEvents(eventType, handler) {
        this.client.subscribe('events', (message) => {
            if (message.payload.type === eventType) {
                handler(message.payload);
            }
        });
    }
    
    getAvailableServices() {
        return Array.from(this.services.values());
    }
    
    async shutdown() {
        this.client.disconnect();
    }
}

// Example usage
class UserService extends MicroserviceClient {
    constructor() {
        super('user-service');
    }
    
    async createUser(userData) {
        // Validate with validation service
        const validation = await this.callService('validation-service', 'validate_user', userData);
        
        if (!validation.payload.valid) {
            throw new Error(`Validation failed: ${validation.payload.errors.join(', ')}`);
        }
        
        // Create user via database service
        const result = await this.callService('database-service', 'create_user', userData);
        
        // Broadcast user created event
        await this.broadcastEvent('user_created', {
            userId: result.payload.user_id,
            userData: userData
        });
        
        return result.payload;
    }
    
    async getUserById(userId) {
        // Try cache first
        try {
            const cached = await this.callService('cache-service', 'get', { key: `user:${userId}` });
            if (cached.payload.found) {
                return cached.payload.data;
            }
        } catch (error) {
            console.warn('Cache service unavailable, falling back to database');
        }
        
        // Get from database
        const result = await this.callService('database-service', 'get_user', { user_id: userId });
        
        // Cache the result
        try {
            await this.callService('cache-service', 'set', {
                key: `user:${userId}`,
                data: result.payload,
                ttl: 3600
            });
        } catch (error) {
            console.warn('Failed to cache user data');
        }
        
        return result.payload;
    }
}

// Start the service
const userService = new UserService();
userService.initialize().then(() => {
    console.log('User service ready');
});
```

### Load Balancer Pattern

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class LoadBalancedClient {
    constructor(serviceType, options = {}) {
        this.serviceType = serviceType;
        this.client = new IPCClient(`${serviceType}-lb-client`, options);
        this.serviceInstances = [];
        this.currentIndex = 0;
        this.strategy = options.strategy || 'round_robin';
    }
    
    async initialize() {
        await this.client.connect();
        
        // Get available service instances
        const response = await this.client.sendRequest('system', {
            action: 'get_service_instances',
            service_type: this.serviceType
        });
        
        this.serviceInstances = response.payload.instances.filter(instance => instance.healthy);
        
        // Subscribe to instance updates
        this.client.subscribe('service_instances', (message) => {
            if (message.payload.service_type === this.serviceType) {
                this.updateInstances(message.payload);
            }
        });
        
        console.log(`Load balancer initialized for ${this.serviceType} with ${this.serviceInstances.length} instances`);
    }
    
    updateInstances(update) {
        const { action, instance } = update;
        
        switch (action) {
            case 'instance_added':
                if (instance.healthy) {
                    this.serviceInstances.push(instance);
                }
                break;
                
            case 'instance_removed':
                this.serviceInstances = this.serviceInstances.filter(i => i.id !== instance.id);
                break;
                
            case 'instance_health_changed':
                if (instance.healthy) {
                    if (!this.serviceInstances.find(i => i.id === instance.id)) {
                        this.serviceInstances.push(instance);
                    }
                } else {
                    this.serviceInstances = this.serviceInstances.filter(i => i.id !== instance.id);
                }
                break;
        }
    }
    
    selectInstance() {
        if (this.serviceInstances.length === 0) {
            throw new Error(`No healthy instances available for ${this.serviceType}`);
        }
        
        let instance;
        
        switch (this.strategy) {
            case 'round_robin':
                instance = this.serviceInstances[this.currentIndex];
                this.currentIndex = (this.currentIndex + 1) % this.serviceInstances.length;
                break;
                
            case 'random':
                instance = this.serviceInstances[Math.floor(Math.random() * this.serviceInstances.length)];
                break;
                
            case 'least_connections':
                instance = this.serviceInstances.reduce((min, current) => 
                    current.connections < min.connections ? current : min
                );
                break;
                
            default:
                instance = this.serviceInstances[0];
        }
        
        return instance;
    }
    
    async makeRequest(action, data, options = {}) {
        const maxRetries = options.retries || 3;
        let lastError;
        
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const instance = this.selectInstance();
                
                const response = await this.client.sendRequest(instance.channel, {
                    action: action,
                    data: data,
                    instance_id: instance.id
                });
                
                return response;
                
            } catch (error) {
                lastError = error;
                console.warn(`Request failed on attempt ${attempt + 1}:`, error.message);
                
                if (attempt < maxRetries - 1) {
                    await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
                }
            }
        }
        
        throw new Error(`All ${maxRetries} attempts failed. Last error: ${lastError.message}`);
    }
}

// Usage example
const processingService = new LoadBalancedClient('data-processor', {
    strategy: 'least_connections',
    host: 'localhost',
    port: 8888
});

processingService.initialize().then(async () => {
    try {
        const result = await processingService.makeRequest('process_data', {
            dataset: 'large_dataset.csv',
            algorithm: 'machine_learning'
        });
        
        console.log('Processing result:', result.payload);
    } catch (error) {
        console.error('Processing failed:', error.message);
    }
});
```

## Advanced Usage

### Connection Pooling

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class IPCConnectionPool {
    constructor(poolName, options = {}) {
        this.poolName = poolName;
        this.minConnections = options.minConnections || 2;
        this.maxConnections = options.maxConnections || 10;
        this.connectionOptions = options.connectionOptions || {};
        
        this.connections = [];
        this.availableConnections = [];
        this.waitingRequests = [];
        this.isInitialized = false;
    }
    
    async initialize() {
        // Create minimum connections
        for (let i = 0; i < this.minConnections; i++) {
            const connection = await this.createConnection(i);
            this.connections.push(connection);
            this.availableConnections.push(connection);
        }
        
        this.isInitialized = true;
        console.log(`✅ Connection pool ${this.poolName} initialized with ${this.minConnections} connections`);
    }
    
    async createConnection(id) {
        const client = new IPCClient(`${this.poolName}-pool-${id}`, {
            ...this.connectionOptions
        });
        
        const connected = await client.connect();
        if (!connected) {
            throw new Error(`Failed to create pool connection ${id}`);
        }
        
        return {
            id: id,
            client: client,
            inUse: false,
            createdAt: Date.now(),
            lastUsed: Date.now()
        };
    }
    
    async getConnection() {
        if (!this.isInitialized) {
            throw new Error('Connection pool not initialized');
        }
        
        // Check for available connection
        if (this.availableConnections.length > 0) {
            const connection = this.availableConnections.pop();
            connection.inUse = true;
            connection.lastUsed = Date.now();
            return connection;
        }
        
        // Create new connection if under max limit
        if (this.connections.length < this.maxConnections) {
            const connection = await this.createConnection(this.connections.length);
            this.connections.push(connection);
            connection.inUse = true;
            return connection;
        }
        
        // Wait for available connection
        return new Promise((resolve) => {
            this.waitingRequests.push(resolve);
        });
    }
    
    releaseConnection(connection) {
        connection.inUse = false;
        
        // Serve waiting request if any
        if (this.waitingRequests.length > 0) {
            const resolve = this.waitingRequests.shift();
            connection.inUse = true;
            connection.lastUsed = Date.now();
            resolve(connection);
        } else {
            this.availableConnections.push(connection);
        }
    }
    
    async executeRequest(channelId, payload, timeout) {
        const connection = await this.getConnection();
        
        try {
            const response = await connection.client.sendRequest(channelId, payload, timeout);
            return response;
        } finally {
            this.releaseConnection(connection);
        }
    }
    
    async shutdown() {
        for (const connection of this.connections) {
            connection.client.disconnect();
        }
        
        this.connections = [];
        this.availableConnections = [];
        this.waitingRequests = [];
        this.isInitialized = false;
    }
    
    getStats() {
        return {
            total: this.connections.length,
            available: this.availableConnections.length,
            inUse: this.connections.filter(c => c.inUse).length,
            waiting: this.waitingRequests.length
        };
    }
}

// Usage
const pool = new IPCConnectionPool('api-pool', {
    minConnections: 3,
    maxConnections: 15,
    connectionOptions: {
        host: 'localhost',
        port: 8888,
        reconnectAttempts: 5
    }
});

pool.initialize().then(async () => {
    // Use the pool for requests
    try {
        const response = await pool.executeRequest('api', {
            action: 'get_data',
            id: 123
        });
        
        console.log('Response:', response.payload);
        console.log('Pool stats:', pool.getStats());
    } catch (error) {
        console.error('Request failed:', error.message);
    }
});
```

### Message Queuing

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class MessageQueue {
    constructor(queueName, options = {}) {
        this.queueName = queueName;
        this.client = new IPCClient(`queue-${queueName}`, options);
        this.processors = new Map();
        this.isProcessing = false;
        this.maxConcurrency = options.maxConcurrency || 5;
        this.retryAttempts = options.retryAttempts || 3;
        this.retryDelay = options.retryDelay || 1000;
    }
    
    async initialize() {
        await this.client.connect();
        
        // Subscribe to queue messages
        this.client.subscribe(`queue:${this.queueName}`, (message) => {
            this.handleQueueMessage(message.payload);
        });
        
        console.log(`Message queue ${this.queueName} initialized`);
    }
    
    async enqueue(jobType, jobData, options = {}) {
        const job = {
            id: this.generateJobId(),
            type: jobType,
            data: jobData,
            priority: options.priority || 0,
            attempts: 0,
            maxAttempts: options.maxAttempts || this.retryAttempts,
            createdAt: Date.now(),
            scheduledFor: options.delay ? Date.now() + options.delay : Date.now()
        };
        
        await this.client.sendRequest('queue_manager', {
            action: 'enqueue',
            queue: this.queueName,
            job: job
        });
        
        return job.id;
    }
    
    registerProcessor(jobType, processorFunction) {
        this.processors.set(jobType, processorFunction);
    }
    
    async handleQueueMessage(message) {
        if (message.type === 'job_available') {
            await this.processJobs();
        }
    }
    
    async processJobs() {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        
        try {
            const response = await this.client.sendRequest('queue_manager', {
                action: 'dequeue',
                queue: this.queueName,
                count: this.maxConcurrency
            });
            
            const jobs = response.payload.jobs || [];
            
            if (jobs.length > 0) {
                await Promise.all(jobs.map(job => this.processJob(job)));
            }
        } catch (error) {
            console.error('Error processing jobs:', error.message);
        } finally {
            this.isProcessing = false;
        }
    }
    
    async processJob(job) {
        const processor = this.processors.get(job.type);
        
        if (!processor) {
            console.error(`No processor registered for job type: ${job.type}`);
            await this.markJobFailed(job, 'No processor available');
            return;
        }
        
        try {
            console.log(`Processing job ${job.id} (${job.type})`);
            
            const result = await processor(job.data);
            
            await this.markJobCompleted(job, result);
            
        } catch (error) {
            console.error(`Job ${job.id} failed:`, error.message);
            
            job.attempts++;
            
            if (job.attempts >= job.maxAttempts) {
                await this.markJobFailed(job, error.message);
            } else {
                await this.retryJob(job);
            }
        }
    }
    
    async markJobCompleted(job, result) {
        await this.client.sendRequest('queue_manager', {
            action: 'job_completed',
            job_id: job.id,
            result: result
        });
    }
    
    async markJobFailed(job, error) {
        await this.client.sendRequest('queue_manager', {
            action: 'job_failed',
            job_id: job.id,
            error: error
        });
    }
    
    async retryJob(job) {
        await this.client.sendRequest('queue_manager', {
            action: 'retry_job',
            job_id: job.id,
            delay: this.retryDelay * job.attempts
        });
    }
    
    generateJobId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    async getQueueStats() {
        const response = await this.client.sendRequest('queue_manager', {
            action: 'get_queue_stats',
            queue: this.queueName
        });
        
        return response.payload;
    }
}

// Usage example
const emailQueue = new MessageQueue('email', {
    maxConcurrency: 3,
    retryAttempts: 3,
    retryDelay: 2000
});

// Register processors
emailQueue.registerProcessor('send_welcome', async (data) => {
    console.log(`Sending welcome email to ${data.email}`);
    // Simulate email sending
    await new Promise(resolve => setTimeout(resolve, 1000));
    return { sent: true, messageId: 'msg-123' };
});

emailQueue.registerProcessor('send_notification', async (data) => {
    console.log(`Sending notification: ${data.subject}`);
    // Simulate email sending
    await new Promise(resolve => setTimeout(resolve, 500));
    return { sent: true, messageId: 'msg-456' };
});

emailQueue.initialize().then(async () => {
    // Enqueue some jobs
    await emailQueue.enqueue('send_welcome', {
        email: 'user@example.com',
        name: 'John Doe'
    });
    
    await emailQueue.enqueue('send_notification', {
        email: 'admin@example.com',
        subject: 'Server maintenance scheduled',
        body: 'Maintenance will begin at 2 AM UTC'
    });
    
    // Start processing
    setInterval(async () => {
        const stats = await emailQueue.getQueueStats();
        console.log('Queue stats:', stats);
    }, 10000);
});
```

## Best Practices

### Error Handling

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class RobustIPCClient {
    constructor(appId, options = {}) {
        this.appId = appId;
        this.client = new IPCClient(appId, {
            reconnectAttempts: 10,
            reconnectDelay: 3000,
            heartbeatInterval: 30000,
            ...options
        });
        
        this.setupErrorHandling();
        this.setupCircuitBreaker();
    }
    
    setupErrorHandling() {
        this.client.onError((error) => {
            console.error(`IPC Error [${this.appId}]:`, error.message);
            
            // Log to monitoring system
            this.logError('ipc_connection_error', error);
        });
        
        this.client.onDisconnected(() => {
            console.warn(`IPC Disconnected [${this.appId}]`);
            
            // Notify monitoring
            this.logEvent('ipc_disconnected');
        });
        
        this.client.onConnected(() => {
            console.log(`IPC Connected [${this.appId}]`);
            
            // Reset circuit breaker on successful connection
            this.circuitBreaker.reset();
            
            this.logEvent('ipc_connected');
        });
    }
    
    setupCircuitBreaker() {
        this.circuitBreaker = {
            failures: 0,
            threshold: 5,
            timeout: 30000,
            state: 'CLOSED', // CLOSED, OPEN, HALF_OPEN
            lastFailTime: null
        };
    }
    
    async makeRequest(channelId, payload, options = {}) {
        // Check circuit breaker
        if (this.circuitBreaker.state === 'OPEN') {
            if (Date.now() - this.circuitBreaker.lastFailTime > this.circuitBreaker.timeout) {
                this.circuitBreaker.state = 'HALF_OPEN';
            } else {
                throw new Error('Circuit breaker is OPEN');
            }
        }
        
        try {
            const response = await this.client.sendRequest(channelId, payload, options.timeout);
            
            // Reset failure count on success
            if (this.circuitBreaker.state === 'HALF_OPEN') {
                this.circuitBreaker.state = 'CLOSED';
            }
            this.circuitBreaker.failures = 0;
            
            return response;
            
        } catch (error) {
            this.circuitBreaker.failures++;
            this.circuitBreaker.lastFailTime = Date.now();
            
            if (this.circuitBreaker.failures >= this.circuitBreaker.threshold) {
                this.circuitBreaker.state = 'OPEN';
                console.error(`Circuit breaker opened for ${this.appId}`);
            }
            
            // Log the error
            this.logError('ipc_request_error', error, {
                channelId,
                payload: JSON.stringify(payload).substr(0, 200)
            });
            
            throw error;
        }
    }
    
    async makeRequestWithRetry(channelId, payload, options = {}) {
        const maxRetries = options.retries || 3;
        const retryDelay = options.retryDelay || 1000;
        const backoffMultiplier = options.backoffMultiplier || 2;
        
        let lastError;
        
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                return await this.makeRequest(channelId, payload, options);
                
            } catch (error) {
                lastError = error;
                
                if (attempt < maxRetries - 1) {
                    const delay = retryDelay * Math.pow(backoffMultiplier, attempt);
                    console.warn(`Request failed, retrying in ${delay}ms (attempt ${attempt + 1}/${maxRetries})`);
                    await this.sleep(delay);
                }
            }
        }
        
        throw new Error(`Request failed after ${maxRetries} attempts: ${lastError.message}`);
    }
    
    async safeRequest(channelId, payload, options = {}) {
        try {
            return await this.makeRequestWithRetry(channelId, payload, options);
        } catch (error) {
            // Return default value or handle gracefully
            if (options.defaultValue !== undefined) {
                console.warn(`Request failed, using default value:`, options.defaultValue);
                return { payload: options.defaultValue };
            }
            
            if (options.throwOnError !== false) {
                throw error;
            }
            
            return null;
        }
    }
    
    logError(type, error, context = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            type: type,
            appId: this.appId,
            error: {
                message: error.message,
                stack: error.stack
            },
            context: context
        };
        
        // Send to logging service or console
        console.error('IPC Error Log:', JSON.stringify(logEntry, null, 2));
        
        // Could send to external monitoring
        // this.sendToMonitoring(logEntry);
    }
    
    logEvent(type, data = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            type: type,
            appId: this.appId,
            data: data
        };
        
        console.log('IPC Event Log:', JSON.stringify(logEntry));
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async connect() {
        return await this.client.connect();
    }
    
    disconnect() {
        this.client.disconnect();
    }
    
    getCircuitBreakerState() {
        return this.circuitBreaker;
    }
}

// Usage
const robustClient = new RobustIPCClient('robust-app');

robustClient.connect().then(async () => {
    // Safe request with default value
    const userData = await robustClient.safeRequest('user_service', {
        action: 'get_user',
        user_id: 123
    }, {
        defaultValue: { name: 'Unknown User' },
        retries: 3,
        timeout: 5000
    });
    
    console.log('User data:', userData.payload);
});
```

### Performance Optimization

```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

class PerformantIPCClient {
    constructor(appId, options = {}) {
        this.appId = appId;
        this.client = new IPCClient(appId, options);
        
        // Request batching
        this.batchQueue = [];
        this.batchTimeout = options.batchTimeout || 10;
        this.maxBatchSize = options.maxBatchSize || 50;
        this.batchTimer = null;
        
        // Response caching
        this.cache = new Map();
        this.cacheTimeout = options.cacheTimeout || 60000; // 1 minute
        
        // Request deduplication
        this.pendingRequests = new Map();
        
        // Performance metrics
        this.metrics = {
            requestCount: 0,
            errorCount: 0,
            cacheHits: 0,
            cacheMisses: 0,
            avgResponseTime: 0,
            batchedRequests: 0
        };
    }
    
    async connect() {
        return await this.client.connect();
    }
    
    // Cached request
    async cachedRequest(channelId, payload, options = {}) {
        const cacheKey = this.generateCacheKey(channelId, payload);
        const ttl = options.cacheTtl || this.cacheTimeout;
        
        // Check cache first
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < ttl) {
            this.metrics.cacheHits++;
            return cached.data;
        }
        
        this.metrics.cacheMisses++;
        
        // Make request
        const response = await this.client.sendRequest(channelId, payload);
        
        // Cache the response
        this.cache.set(cacheKey, {
            data: response,
            timestamp: Date.now()
        });
        
        // Clean up old cache entries periodically
        this.cleanupCache();
        
        return response;
    }
    
    // Batched request
    async batchedRequest(channelId, payload, options = {}) {
        return new Promise((resolve, reject) => {
            this.batchQueue.push({
                channelId,
                payload,
                options,
                resolve,
                reject,
                timestamp: Date.now()
            });
            
            // Schedule batch processing
            if (!this.batchTimer) {
                this.batchTimer = setTimeout(() => {
                    this.processBatch();
                }, this.batchTimeout);
            }
            
            // Process immediately if batch is full
            if (this.batchQueue.length >= this.maxBatchSize) {
                clearTimeout(this.batchTimer);
                this.processBatch();
            }
        });
    }
    
    // Deduplicated request
    async deduplicatedRequest(channelId, payload, options = {}) {
        const requestKey = this.generateRequestKey(channelId, payload);
        
        // Check if same request is already pending
        if (this.pendingRequests.has(requestKey)) {
            return await this.pendingRequests.get(requestKey);
        }
        
        // Create new request promise
        const requestPromise = this.measureRequest(async () => {
            return await this.client.sendRequest(channelId, payload, options.timeout);
        });
        
        // Store pending request
        this.pendingRequests.set(requestKey, requestPromise);
        
        try {
            const result = await requestPromise;
            return result;
        } finally {
            // Clean up pending request
            this.pendingRequests.delete(requestKey);
        }
    }
    
    async processBatch() {
        if (this.batchQueue.length === 0) return;
        
        const batch = this.batchQueue.splice(0, this.maxBatchSize);
        this.batchTimer = null;
        
        try {
            // Group by channel
            const channelGroups = batch.reduce((groups, request) => {
                if (!groups[request.channelId]) {
                    groups[request.channelId] = [];
                }
                groups[request.channelId].push(request);
                return groups;
            }, {});
            
            // Process each channel group
            const promises = Object.entries(channelGroups).map(([channelId, requests]) => {
                return this.processBatchForChannel(channelId, requests);
            });
            
            await Promise.all(promises);
            
            this.metrics.batchedRequests += batch.length;
            
        } catch (error) {
            // Reject all requests in batch
            batch.forEach(request => {
                request.reject(error);
            });
        }
        
        // Process remaining requests if any
        if (this.batchQueue.length > 0) {
            this.batchTimer = setTimeout(() => {
                this.processBatch();
            }, this.batchTimeout);
        }
    }
    
    async processBatchForChannel(channelId, requests) {
        try {
            const batchPayload = {
                action: 'batch_process',
                requests: requests.map((req, index) => ({
                    id: index,
                    payload: req.payload
                }))
            };
            
            const response = await this.client.sendRequest(channelId, batchPayload);
            
            // Distribute responses
            if (response.payload.responses) {
                response.payload.responses.forEach((resp, index) => {
                    if (requests[index]) {
                        requests[index].resolve({ payload: resp });
                    }
                });
            } else {
                // Fallback: process individually
                await this.processBatchIndividually(channelId, requests);
            }
            
        } catch (error) {
            // Fallback: process individually
            await this.processBatchIndividually(channelId, requests);
        }
    }
    
    async processBatchIndividually(channelId, requests) {
        const promises = requests.map(async (request) => {
            try {
                const response = await this.client.sendRequest(channelId, request.payload);
                request.resolve(response);
            } catch (error) {
                request.reject(error);
            }
        });
        
        await Promise.allSettled(promises);
    }
    
    async measureRequest(requestFn) {
        const startTime = Date.now();
        this.metrics.requestCount++;
        
        try {
            const result = await requestFn();
            
            // Update average response time
            const responseTime = Date.now() - startTime;
            this.metrics.avgResponseTime = (
                (this.metrics.avgResponseTime * (this.metrics.requestCount - 1)) + responseTime
            ) / this.metrics.requestCount;
            
            return result;
            
        } catch (error) {
            this.metrics.errorCount++;
            throw error;
        }
    }
    
    generateCacheKey(channelId, payload) {
        return `${channelId}:${JSON.stringify(payload)}`;
    }
    
    generateRequestKey(channelId, payload) {
        return `${channelId}:${JSON.stringify(payload)}`;
    }
    
    cleanupCache() {
        if (this.cache.size > 1000) { // Cleanup when cache gets large
            const now = Date.now();
            for (const [key, value] of this.cache.entries()) {
                if (now - value.timestamp > this.cacheTimeout) {
                    this.cache.delete(key);
                }
            }
        }
    }
    
    getMetrics() {
        return {
            ...this.metrics,
            cacheSize: this.cache.size,
            pendingRequests: this.pendingRequests.size,
            queuedBatches: this.batchQueue.length
        };
    }
    
    clearCache() {
        this.cache.clear();
    }
    
    disconnect() {
        if (this.batchTimer) {
            clearTimeout(this.batchTimer);
        }
        this.client.disconnect();
    }
}

// Usage
const performantClient = new PerformantIPCClient('perf-app', {
    batchTimeout: 5,
    maxBatchSize: 25,
    cacheTimeout: 30000
});

performantClient.connect().then(async () => {
    // Cached request
    const userData = await performantClient.cachedRequest('user_service', {
        action: 'get_user',
        user_id: 123
    }, { cacheTtl: 60000 });
    
    // Batched requests
    const promises = [];
    for (let i = 0; i < 10; i++) {
        promises.push(
            performantClient.batchedRequest('data_service', {
                action: 'process_item',
                item_id: i
            })
        );
    }
    
    const results = await Promise.all(promises);
    console.log('Batch results:', results.length);
    
    // Performance metrics
    console.log('Metrics:', performantClient.getMetrics());
});
```

## Migration from v1.1.0

### What Changed

**v1.1.0 was fundamentally broken** due to:
- ❌ Used WebSocket protocol (incompatible with Python TCP servers)
- ❌ Module system conflicts (CommonJS/ESM mixing)
- ❌ Complex build system causing distribution issues
- ❌ Dependency resolution problems

**v1.1.1 fixes everything:**
- ✅ Uses TCP sockets (correct protocol for Python servers)
- ✅ Pure CommonJS - no module conflicts
- ✅ Simplified architecture - no build dependencies
- ✅ Zero external dependencies

### Migration Steps

1. **Update the package:**
```bash
npm uninstall @ifesol/ipc-framework-nodejs
npm install @ifesol/ipc-framework-nodejs@latest
```

2. **Update import syntax:**
```javascript
// OLD (v1.1.0) - BROKEN
import { IPCClient } from '@ifesol/ipc-framework-nodejs'; // Failed to load

// NEW (v1.1.1) - WORKING
const { IPCClient } = require('@ifesol/ipc-framework-nodejs'); // ✅ Works
```

3. **Update connection code:**
```javascript
// OLD (v1.1.0) - WebSocket (wrong protocol)
const client = new IPCClient('my-app', {
    host: 'ws://localhost:8888'  // ❌ WebSocket URL
});

// NEW (v1.1.1) - TCP (correct protocol)
const client = new IPCClient('my-app', {
    host: 'localhost',  // ✅ TCP host
    port: 8888          // ✅ TCP port
});
```

4. **Remove TypeScript references:**
```javascript
// OLD (v1.1.0) - TypeScript imports
import { IPCClient, MessageType } from '@ifesol/ipc-framework-nodejs';

// NEW (v1.1.1) - CommonJS
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');
// MessageType not needed - use strings directly
```

5. **Test the connection:**
```javascript
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');

const client = new IPCClient('test-app');
client.connect().then(async (connected) => {
    if (connected) {
        console.log('✅ v1.1.1 working correctly!');
        
        const response = await client.sendRequest('system', { action: 'ping' });
        console.log('Ping response:', response.payload);
        
        client.disconnect();
    } else {
        console.log('❌ Connection failed');
    }
});
```

### Breaking Changes

1. **Module System**: Must use `require()` instead of `import`
2. **Protocol**: Now uses TCP instead of WebSocket
3. **Types**: No TypeScript types (simplified to JavaScript)
4. **Dependencies**: Zero external dependencies

### Compatibility

- ✅ **Python servers**: Works with ipc-framework v1.1.0+
- ✅ **Node.js**: Requires Node.js 16+
- ✅ **Operating Systems**: Windows, macOS, Linux
- ❌ **Browsers**: Not supported (use Python HTTP API instead)

## Troubleshooting

### Common Issues

#### Connection Failures

```javascript
// Problem: Cannot connect to Python server
const client = new IPCClient('my-app');
const connected = await client.connect();
if (!connected) {
    console.log('Connection failed');
}

// Solution: Check Python server is running
// 1. Start Python server:
//    python -m ipc_framework.demo
// 2. Verify port is correct (default 8888)
// 3. Check firewall settings
```

#### Module Loading Errors

```javascript
// Problem: require() fails
const { IPCClient } = require('@ifesol/ipc-framework-nodejs');
// Error: Cannot find module

// Solution: Update to v1.1.1+
// npm uninstall @ifesol/ipc-framework-nodejs
// npm install @ifesol/ipc-framework-nodejs@latest
```

#### Request Timeouts

```javascript
// Problem: Requests timeout
const response = await client.sendRequest('api', { action: 'slow_operation' });
// Error: Request timeout

// Solution: Increase timeout
const response = await client.sendRequest('api', {
    action: 'slow_operation'
}, 30000); // 30 second timeout
```

#### Memory Leaks

```javascript
// Problem: Memory usage increases over time

// Solution: Properly disconnect and cleanup
process.on('SIGINT', () => {
    client.disconnect();
    process.exit(0);
});

// For Express.js
app.on('close', () => {
    client.disconnect();
});
```

### Debug Mode

```javascript
// Enable debug logging
const client = new IPCClient('debug-app', {
    host: 'localhost',
    port: 8888
});

// Log all events
client.onConnected(() => console.log('🟢 Connected'));
client.onDisconnected(() => console.log('🔴 Disconnected'));
client.onError((error) => console.log('❌ Error:', error.message));

// Monitor connection health
setInterval(async () => {
    if (client.connected) {
        try {
            const isHealthy = await client.healthCheck();
            console.log('Health check:', isHealthy ? '✅' : '❌');
        } catch (error) {
            console.log('Health check failed:', error.message);
        }
    }
}, 10000);
```

### Performance Issues

```javascript
// Use connection pooling for high throughput
const pool = new IPCConnectionPool('high-throughput', {
    minConnections: 5,
    maxConnections: 20
});

await pool.initialize();

// Use batching for multiple requests
const batchClient = new PerformantIPCClient('batch-app', {
    batchTimeout: 10,
    maxBatchSize: 50
});

// Monitor metrics
setInterval(() => {
    console.log('Metrics:', batchClient.getMetrics());
}, 5000);
```

## Support

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/ifesol/ipc-framework-nodejs/issues)
- **Documentation**: [Complete API reference](https://github.com/ifesol/ipc-framework-nodejs/blob/main/docs/)
- **Python Package**: [ipc-framework on PyPI](https://pypi.org/project/ipc-framework/)

---

**🎉 The Node.js package is now working correctly in v1.1.1!** 

Connect your Node.js applications to Python backends with confidence using our **fixed TCP implementation**. 