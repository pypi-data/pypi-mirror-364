# IPC Framework JS

[![npm version](https://badge.fury.io/js/ipc-framework-js.svg)](https://www.npmjs.com/package/ipc-framework-js)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, TypeScript-first Inter-Process Communication framework for JavaScript/TypeScript applications. Works seamlessly in both **Node.js** (backend) and **browser** (frontend) environments using WebSockets.

## 🚀 Features

- **🌐 Universal**: Works in both Node.js and browser environments
- **📝 TypeScript First**: Full TypeScript support with comprehensive type definitions
- **🔄 Real-time**: WebSocket-based communication for instant message delivery
- **🏗️ Hierarchical**: Organized by applications → channels → messages
- **📡 Multiple Message Types**: Request/Response, Pub/Sub, Notifications
- **🔗 Auto-reconnection**: Built-in reconnection logic with exponential backoff
- **💗 Heartbeat**: Keep-alive mechanism to maintain connections
- **🎯 Type-safe**: Fully typed APIs for better developer experience
- **📦 Dual Package**: Separate builds for Node.js and browsers

## 📦 Installation

```bash
npm install ipc-framework-js
```

For Node.js usage, you'll also need the WebSocket library:

```bash
npm install ws
npm install --save-dev @types/ws  # If using TypeScript
```

## 🎯 Quick Start

### Server (Node.js)

```typescript
import { IPCServer, MessageType } from 'ipc-framework-js';

// Create server
const server = new IPCServer({
  host: 'localhost',
  port: 8888,
  maxConnections: 100
});

// Create application and channels
const chatApp = server.createApplication('chat_app', 'Chat Application');
const generalChannel = chatApp.createChannel('general');

// Set up message handler
generalChannel.setHandler(MessageType.REQUEST, (message) => {
  console.log('Received message:', message.payload);
  
  // Broadcast to all subscribers
  server.handlePublish(message, generalChannel);
});

// Start server
await server.start();
console.log('🚀 IPC Server started on ws://localhost:8888');
```

### Client (Node.js)

```typescript
import { IPCClient, MessageType } from 'ipc-framework-js';

// Create client
const client = new IPCClient('chat_app', {
  host: 'localhost',
  port: 8888,
  reconnectAttempts: 5
});

// Connect
await client.connect();

// Subscribe to messages
client.subscribe('general', (message) => {
  console.log('Received:', message.payload);
});

// Send message
client.request('general', {
  username: 'john',
  text: 'Hello World!'
});
```

### Client (Browser)

```html
<!DOCTYPE html>
<html>
<head>
  <title>IPC Client</title>
  <script src="./node_modules/ipc-framework-js/dist/browser/index.js"></script>
</head>
<body>
  <script>
    // Create client
    const client = new IPCFramework.IPCClient('chat_app', {
      host: 'localhost',
      port: 8888
    });

    // Connect and use
    client.connect().then(() => {
      console.log('Connected!');
      
      // Subscribe to messages
      client.subscribe('general', (message) => {
        console.log('Received:', message.payload);
      });
      
      // Send message
      client.request('general', {
        username: 'browser_user',
        text: 'Hello from browser!'
      });
    });
  </script>
</body>
</html>
```

## 📚 API Reference

### Server API

#### `IPCServer`

```typescript
class IPCServer {
  constructor(options?: IServerOptions)
  
  // Server lifecycle
  async start(): Promise<void>
  async stop(): Promise<void>
  
  // Application management
  createApplication(appId: string, name?: string): Application
  getApplication(appId: string): Application | undefined
  removeApplication(appId: string): boolean
  
  // Statistics
  getStats(): IServerStats
  listApplications(): Map<string, any>
}
```

#### Server Options

```typescript
interface IServerOptions {
  host?: string;          // Default: 'localhost'
  port?: number;          // Default: 8888
  maxConnections?: number; // Default: 100
  heartbeatInterval?: number; // Default: 30000ms
}
```

### Client API

#### `IPCClient`

```typescript
class IPCClient {
  constructor(appId: string, options?: IClientOptions)
  
  // Connection management
  async connect(): Promise<boolean>
  disconnect(): void
  isConnected(): boolean
  
  // Messaging
  subscribe(channelId: string, handler?: MessageHandler): boolean
  unsubscribe(channelId: string): boolean
  request(channelId: string, data: any): string
  notify(channelId: string, data: any): string
  publish(channelId: string, data: any): string
  
  // Advanced messaging
  async sendRequest(channelId: string, data: any, timeout?: number): Promise<Message | null>
  sendRequestAsync(channelId: string, data: any, callback: Function): string
  
  // Utilities
  async ping(timeout?: number): Promise<boolean>
  getConnectionInfo(): IConnectionInfo
  
  // Event handlers
  onConnected(handler: () => void): void
  onDisconnected(handler: () => void): void
  onError(handler: (error: Error) => void): void
}
```

#### Client Options

```typescript
interface IClientOptions {
  host?: string;              // Default: 'localhost'
  port?: number;              // Default: 8888
  connectionTimeout?: number;  // Default: 10000ms
  reconnectAttempts?: number;  // Default: 5
  reconnectDelay?: number;     // Default: 1000ms
  heartbeatInterval?: number;  // Default: 30000ms
}
```

### Message Types

```typescript
enum MessageType {
  REQUEST = 'request',         // Request-response pattern
  RESPONSE = 'response',       // Response to a request
  NOTIFICATION = 'notification', // One-way message
  SUBSCRIBE = 'subscribe',     // Subscribe to channel
  UNSUBSCRIBE = 'unsubscribe', // Unsubscribe from channel
  PUBLISH = 'publish'          // Publish to subscribers
}
```

### Core Classes

#### `Message`

```typescript
class Message {
  readonly messageId: string;
  readonly appId: string;
  readonly channelId: string;
  readonly messageType: MessageType;
  readonly payload: any;
  readonly timestamp: number;
  readonly replyTo?: string;
  
  // Serialization
  toJSON(): string
  toObject(): IMessage
  
  // Static methods
  static fromJSON(json: string): Message
  static fromObject(data: IMessage): Message
  
  // Utility methods
  createResponse(payload: any): Message
  isResponse(): boolean
  isRequest(): boolean
  // ... more utility methods
}
```

#### `Application`

```typescript
class Application {
  readonly appId: string;
  readonly name: string;
  readonly createdAt: number;
  
  // Channel management
  createChannel(channelId: string): Channel
  getChannel(channelId: string): Channel | undefined
  removeChannel(channelId: string): boolean
  listChannels(): string[]
  
  // Statistics
  getStats(): IApplicationStats
  getTotalConnectionCount(): number
}
```

#### `Channel`

```typescript
class Channel {
  readonly channelId: string;
  readonly appId: string;
  readonly createdAt: number;
  
  // Subscriber management
  addSubscriber(connectionId: string): void
  removeSubscriber(connectionId: string): boolean
  getSubscribers(): string[]
  
  // Message handling
  setHandler(messageType: MessageType, handler: MessageHandler): void
  removeHandler(messageType: MessageType): boolean
  executeHandler(message: Message): Promise<boolean>
}
```

## 🏗️ Architecture

The IPC Framework follows a hierarchical structure:

```
Server
├── Application (chat_app)
│   ├── Channel (general)
│   ├── Channel (tech_talk)
│   └── Channel (random)
├── Application (file_share)
│   ├── Channel (upload)
│   └── Channel (download)
└── Application (monitoring)
    ├── Channel (metrics)
    └── Channel (alerts)
```

### Message Flow

1. **Client connects** to server with an `appId`
2. **Client subscribes** to channels within that application
3. **Messages are routed** based on `appId` → `channelId`
4. **Handlers process** messages based on message type
5. **Responses/broadcasts** are sent back to relevant subscribers

## 🛠️ Development

### Building

```bash
# Install dependencies
npm install

# Build for all environments
npm run build

# Build for specific environments
npm run build:node      # Node.js build
npm run build:browser   # Browser build
npm run build:types     # TypeScript declarations
```

### Development Mode

```bash
# Watch mode for development
npm run dev

# Run examples
npm run example:server    # Start example server
npm run example:chat     # Start chat client
npm run example:browser  # Start browser demo
```

### Testing

```bash
# Run tests
npm test

# Watch mode
npm run test:watch
```

## 📋 Examples

### Chat Application

Complete chat application with multiple channels:

- **Server**: `examples/node/server.js`
- **Client**: `examples/node/chat-client.js`
- **Browser**: `examples/browser/index.html`

### File Sharing

File upload/download with progress tracking:

```bash
# Terminal 1: Start server
npm run example:server

# Terminal 2: Start file client
node examples/node/file-client.js
```

### System Monitoring

Real-time metrics and alerting:

```bash
# Start monitoring client
node examples/node/monitoring-client.js
```

## 🌐 Browser Usage

### ES Modules (Modern)

```html
<script type="module">
  import { IPCClient } from './node_modules/ipc-framework-js/dist/browser/index.esm.js';
  
  const client = new IPCClient('my_app');
  // Use client...
</script>
```

### UMD (Universal)

```html
<script src="./node_modules/ipc-framework-js/dist/browser/index.js"></script>
<script>
  const client = new IPCFramework.IPCClient('my_app');
  // Use client...
</script>
```

### With Bundlers

Works with Webpack, Rollup, Vite, etc.:

```typescript
import { IPCClient } from 'ipc-framework-js';

// Bundler will automatically use browser build
const client = new IPCClient('my_app');
```

## 🔧 Configuration

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  }
}
```

### Environment Detection

The library automatically detects the environment and uses appropriate WebSocket implementation:

- **Node.js**: Uses `ws` package
- **Browser**: Uses native `WebSocket`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [NPM Package](https://www.npmjs.com/package/ipc-framework-js)
- [GitHub Repository](https://github.com/your-username/ipc-framework-js)
- [Documentation](https://github.com/your-username/ipc-framework-js#readme)
- [Issues](https://github.com/your-username/ipc-framework-js/issues)

## 🙏 Acknowledgments

Inspired by modern real-time communication needs and built with developer experience in mind. 