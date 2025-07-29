# API Reference - IPC Framework

Complete API documentation for both Python and JavaScript/TypeScript packages.

## 🚨 **Version 1.1.0 Critical Updates**

**Python Package**: Please upgrade to v1.1.0 immediately for working functionality:
```bash
pip install --upgrade ipc-framework
```

### ✅ **Fixed APIs in v1.1.0:**
- `Message.create_response()` - **NOW WORKING** (was missing in v1.0.0)
- Client socket operations - **NO MORE DEADLOCKS** 
- Request/response pattern - **FULLY FUNCTIONAL**
- Bidirectional communication - **WORKING PERFECTLY**

## Python API Reference

### Core Classes

#### FrameworkServer

Main server class for handling IPC communications.

```python
class FrameworkServer:
    def __init__(self, host="localhost", port=8888, max_connections=100)
```

**Parameters:**
- `host` (str): Server bind address
- `port` (int): Server port
- `max_connections` (int): Maximum concurrent connections

**Methods:**

##### `start() -> None`
Start the IPC server.

```python
server.start()
```

##### `stop() -> None`
Stop the IPC server gracefully.

```python
server.stop()
```

##### `create_application(app_id: str, name: str = None) -> Application`
Create a new application.

```python
app = server.create_application("my_app", "My Application")
```

##### `get_application(app_id: str) -> Optional[Application]`
Get an existing application by ID.

##### `list_applications() -> Dict[str, Dict]`
Get information about all applications.

##### `get_stats() -> Dict`
Get server statistics.

#### FrameworkClient

Client class for connecting to IPC server.

```python
class FrameworkClient:
    def __init__(self, app_id: str, host="localhost", port=8888, connection_timeout=10.0)
```

**Parameters:**
- `app_id` (str): Application to connect to
- `host` (str): Server address
- `port` (int): Server port
- `connection_timeout` (float): Connection timeout in seconds

**Methods:**

##### `connect() -> bool`
Connect to the IPC server.

##### `disconnect() -> None`
Disconnect from the server.

##### `send_request(channel_id: str, data: Any, timeout: float = 5.0) -> Optional[Message]`
Send a request and wait for response.

##### `subscribe(channel_id: str, handler: Callable = None) -> bool`
Subscribe to a channel.

##### `publish(channel_id: str, data: Any) -> str`
Publish data to a channel.

#### Message

Represents a message in the IPC system.

```python
@dataclass
class Message:
    message_id: str
    app_id: str
    channel_id: str
    message_type: MessageType
    payload: Any
    timestamp: float
    reply_to: Optional[str] = None
```

**Methods:**

##### `to_json() -> str`
Serialize message to JSON string.

##### `from_json(json_str: str) -> Message` (classmethod)
Deserialize message from JSON string.

##### `create_response(payload: Any) -> Message`
Create a response message to this message.

#### MessageType

Enumeration of message types.

```python
class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PUBLISH = "publish"
```

## JavaScript/TypeScript API Reference

### IPCClient

Main client class for connecting to IPC servers.

```typescript
class IPCClient {
  constructor(appId: string, options?: IClientOptions)
}
```

**Parameters:**
- `appId` (string): Application identifier to connect to
- `options` (IClientOptions): Client configuration

#### IClientOptions Interface

```typescript
interface IClientOptions {
  host?: string;              // Server host (default: 'localhost')
  port?: number;              // Server port (default: 8888)
  connectionTimeout?: number;  // Connection timeout ms (default: 10000)
  reconnectAttempts?: number;  // Max reconnection attempts (default: 5)
  reconnectDelay?: number;     // Reconnect delay ms (default: 1000)
  heartbeatInterval?: number;  // Heartbeat interval ms (default: 30000)
}
```

#### Connection Methods

##### `connect(): Promise<boolean>`
Connect to the IPC server.

```typescript
const success = await client.connect();
```

##### `disconnect(): void`
Disconnect from the server.

##### `isConnected(): boolean`
Check connection status.

#### Messaging Methods

##### `subscribe(channelId: string, handler?: MessageHandler): boolean`
Subscribe to a channel with optional message handler.

```typescript
client.subscribe('notifications', (message) => {
  console.log('Notification:', message.payload);
});
```

##### `unsubscribe(channelId: string): boolean`
Unsubscribe from a channel.

##### `request(channelId: string, data: any): string`
Send a request message and return message ID.

##### `notify(channelId: string, data: any): string`
Send a notification message.

##### `publish(channelId: string, data: any): string`
Publish data to all channel subscribers.

##### `sendRequest(channelId: string, data: any, timeout?: number): Promise<Message | null>`
Send request and wait for response.

```typescript
const response = await client.sendRequest('api', {
  endpoint: 'users',
  method: 'GET'
}, 5000);
```

##### `sendRequestAsync(channelId: string, data: any, callback: Function): string`
Send async request with callback.

#### Utility Methods

##### `ping(timeout?: number): Promise<boolean>`
Ping server to check connectivity.

##### `getConnectionInfo(): IConnectionInfo`
Get connection information.

#### Event Handlers

##### `onConnected(handler: () => void): void`
Set connected event handler.

##### `onDisconnected(handler: () => void): void`
Set disconnected event handler.

##### `onError(handler: (error: Error) => void): void`
Set error event handler.

### Message Class

Represents a message in the IPC system.

```typescript
class Message {
  readonly messageId: string;
  readonly appId: string;
  readonly channelId: string;
  readonly messageType: MessageType;
  readonly payload: any;
  readonly timestamp: number;
  readonly replyTo?: string;
}
```

#### Methods

##### `toJSON(): string`
Serialize message to JSON string.

##### `toObject(): IMessage`
Convert message to plain object.

##### `createResponse(payload: any): Message`
Create a response message.

##### `isResponse(): boolean`
Check if message is a response.

##### `isRequest(): boolean`
Check if message is a request.

##### Static Methods

##### `fromJSON(json: string): Message`
Deserialize message from JSON string.

##### `fromObject(data: IMessage): Message`
Create message from plain object.

### MessageType Enum

```typescript
enum MessageType {
  REQUEST = 'request',
  RESPONSE = 'response',
  NOTIFICATION = 'notification',
  SUBSCRIBE = 'subscribe',
  UNSUBSCRIBE = 'unsubscribe',
  PUBLISH = 'publish'
}
```

### Type Definitions

#### IMessage Interface

```typescript
interface IMessage {
  messageId: string;
  appId: string;
  channelId: string;
  messageType: MessageType;
  payload: any;
  timestamp: number;
  replyTo?: string | undefined;
}
```

#### IConnectionInfo Interface

```typescript
interface IConnectionInfo {
  connectionId: string;
  appId: string;
  connected: boolean;
  host: string;
  port: number;
  subscribedChannels: string[];
}
```

#### MessageHandler Type

```typescript
type MessageHandler = (message: IMessage) => void | Promise<void>;
```

### Utility Functions

#### Environment Detection

```typescript
function detectWebSocketEnvironment(): IWebSocketEnvironment
```

Returns information about the current environment and WebSocket implementation.

#### WebSocket Creation

```typescript
function createWebSocket(url: string, protocols?: string | string[]): any
```

Creates a WebSocket instance appropriate for the current environment.

#### WebSocket States

```typescript
function getWebSocketStates(): { [key: string]: number }
```

Returns WebSocket state constants for the current environment.

## Error Handling

### Python Exceptions

```python
from ipc_framework.exceptions import (
    IPCError,           # Base exception
    ConnectionError,    # Connection issues
    RoutingError,       # Message routing failures
    SerializationError  # Message serialization issues
)
```

### JavaScript/TypeScript Errors

The JavaScript client throws standard Error objects with descriptive messages:

```typescript
try {
  await client.connect();
} catch (error) {
  if (error.message.includes('WebSocket')) {
    // Handle WebSocket-specific errors
  } else if (error.message.includes('timeout')) {
    // Handle timeout errors
  }
}
```

## Communication Patterns

### Request/Response Pattern

**Python Server:**
```python
def handle_request(message):
    # Process request
    result = process_data(message.payload)
    
    # Send response
    response = message.create_response(result)
    server.send_to_connection(connection, response)
```

**JavaScript Client:**
```typescript
const response = await client.sendRequest('api', {
  action: 'get_users'
});
console.log(response?.payload);
```

### Publish/Subscribe Pattern

**Python Server:**
```python
# Publish to all subscribers
server._handle_publish(message, channel)
```

**JavaScript Client:**
```typescript
// Subscribe
client.subscribe('notifications', (message) => {
  console.log('Notification:', message.payload);
});

// Publish
client.publish('announcements', {
  title: 'System Update',
  message: 'Maintenance scheduled'
});
```

### Notification Pattern

**Python Server:**
```python
# Send one-way notification
notification = Message(
    app_id="my_app",
    channel_id="events",
    message_type=MessageType.NOTIFICATION,
    payload={"event": "user_login"}
)
server._handle_publish(notification, events_channel)
```

**JavaScript Client:**
```typescript
// Send notification
client.notify('events', {
  type: 'user_action',
  userId: 'user123',
  action: 'login'
});
```

## Configuration Examples

### Python Server Configuration

```python
server = FrameworkServer(
    host="0.0.0.0",         # Bind to all interfaces
    port=8888,              # Custom port
    max_connections=500     # High concurrency
)
```

### JavaScript Client Configuration

```typescript
const client = new IPCClient('my_app', {
  host: 'production-server.com',
  port: 8888,
  connectionTimeout: 15000,    // 15 seconds
  reconnectAttempts: 10,       // Aggressive reconnection
  reconnectDelay: 2000,        // 2 second delay
  heartbeatInterval: 10000     // 10 second heartbeat
});
```

## Best Practices

### Connection Management

**Python:**
```python
# Always use try/finally for cleanup
client = FrameworkClient("my_app")
try:
    if client.connect():
        # Use client
        pass
finally:
    client.disconnect()
```

**JavaScript:**
```typescript
// Use async/await with proper cleanup
const client = new IPCClient('my_app');
try {
  await client.connect();
  // Use client
} finally {
  client.disconnect();
}
```

### Error Handling

**Python:**
```python
from ipc_framework.exceptions import ConnectionError

try:
    response = client.send_request("api", {"action": "test"})
except ConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**JavaScript:**
```typescript
try {
  const response = await client.sendRequest('api', { action: 'test' });
  if (!response) {
    throw new Error('Request timeout');
  }
} catch (error) {
  console.error('Request failed:', error.message);
}
```

### Resource Cleanup

**Python:**
```python
import atexit

def cleanup():
    client.disconnect()
    server.stop()

atexit.register(cleanup)
```

**JavaScript:**
```typescript
// Browser
window.addEventListener('beforeunload', () => {
  client.disconnect();
});

// Node.js
process.on('exit', () => {
  client.disconnect();
});
``` 