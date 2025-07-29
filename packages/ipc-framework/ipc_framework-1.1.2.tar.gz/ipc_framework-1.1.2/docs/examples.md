# Examples - IPC Framework

Comprehensive examples showing how to use both Python and JavaScript packages together.

## 🚨 **IMPORTANT: Use Version 1.1.0 for Working Examples**

**All examples require Python v1.1.0 and Node.js client to function properly:**
```bash
pip install --upgrade ipc-framework       # Python server
npm install @ifesol/ipc-framework-nodejs  # Node.js client
```

**v1.0.0 examples will not work due to critical bugs. v1.1.0 examples are fully functional.**

## Table of Contents

- [Basic Setup](#basic-setup)
- [Chat Application](#chat-application)
- [API Server](#api-server)
- [File Transfer](#file-transfer)
- [Real-time Dashboard](#real-time-dashboard)
- [Multi-User Collaboration](#multi-user-collaboration)

## Basic Setup

### Python Server + JavaScript Client

**Python Server (server.py):**
```python
from ipc_framework import FrameworkServer, MessageType
import time

def main():
    # Create server
    server = FrameworkServer(host="localhost", port=8888)
    
    # Create application
    app = server.create_application("demo_app", "Demo Application")
    
    # Create API channel
    api_channel = app.create_channel("api")
    
    # Handle API requests
    def handle_api_request(message):
        action = message.payload.get('action')
        
        if action == 'get_time':
            response_data = {'time': time.time(), 'message': 'Current server time'}
        elif action == 'echo':
            response_data = {'echo': message.payload.get('data')}
        else:
            response_data = {'error': f'Unknown action: {action}'}
        
        # Send response back
        response = message.create_response(response_data)
        connection = server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        if connection:
            server.send_to_connection(connection, response)
    
    api_channel.set_handler(MessageType.REQUEST, handle_api_request)
    
    # Start server
    server.start()
    print("🚀 Demo server running on localhost:8888")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped")

if __name__ == "__main__":
    main()
```

**JavaScript Client (client.js):**
```javascript
const { IPCClient } = require('@ifesol/ipc-framework-js');

async function main() {
    // Create client
    const client = new IPCClient('demo_app', {
        host: 'localhost',
        port: 8888
    });
    
    // Set up event handlers
    client.onConnected(() => {
        console.log('✅ Connected to server');
    });
    
    client.onDisconnected(() => {
        console.log('❌ Disconnected from server');
    });
    
    // Connect
    const connected = await client.connect();
    if (!connected) {
        console.error('Failed to connect');
        return;
    }
    
    // Test API calls
    try {
        // Get server time
        const timeResponse = await client.sendRequest('api', {
            action: 'get_time',
            connection_id: client.connectionId
        });
        console.log('Server time:', timeResponse?.payload);
        
        // Echo test
        const echoResponse = await client.sendRequest('api', {
            action: 'echo',
            data: 'Hello from JavaScript!',
            connection_id: client.connectionId
        });
        console.log('Echo response:', echoResponse?.payload);
        
    } catch (error) {
        console.error('API call failed:', error);
    }
    
    // Disconnect
    client.disconnect();
}

main();
```

**Run the example:**
```bash
# Terminal 1: Start Python server
python server.py

# Terminal 2: Run JavaScript client
node client.js
```

## Chat Application

### Python Chat Server

```python
from ipc_framework import FrameworkServer, MessageType, Message
import time
import json

class ChatServer:
    def __init__(self):
        self.server = FrameworkServer(host="localhost", port=8888)
        self.users = {}  # connection_id -> user_info
        self.channels = ['general', 'tech', 'random']
        self.setup_chat()
    
    def setup_chat(self):
        # Create chat application
        app = self.server.create_application("chat_app", "Chat Application")
        
        # Create channels
        for channel_name in self.channels:
            channel = app.create_channel(channel_name)
            channel.set_handler(MessageType.REQUEST, self.handle_chat_message)
        
        # Create user management channel
        user_channel = app.create_channel("users")
        user_channel.set_handler(MessageType.REQUEST, self.handle_user_action)
        user_channel.set_handler(MessageType.NOTIFICATION, self.handle_user_notification)
    
    def handle_user_action(self, message):
        action = message.payload.get('action')
        connection_id = message.payload.get('connection_id')
        
        if action == 'join':
            username = message.payload.get('username')
            self.users[connection_id] = {
                'username': username,
                'joined_at': time.time(),
                'channels': ['general']
            }
            
            # Notify all users
            self.broadcast_user_list()
            
            # Send welcome message
            response = message.create_response({
                'success': True,
                'message': f'Welcome {username}!',
                'channels': self.channels
            })
        
        elif action == 'leave':
            if connection_id in self.users:
                username = self.users[connection_id]['username']
                del self.users[connection_id]
                self.broadcast_user_list()
                return
        
        # Send response
        connection = self.server.connection_manager.get_connection(connection_id)
        if connection:
            self.server.send_to_connection(connection, response)
    
    def handle_chat_message(self, message):
        connection_id = message.payload.get('connection_id')
        if connection_id not in self.users:
            return
        
        user = self.users[connection_id]
        username = user['username']
        text = message.payload.get('text', '')
        
        print(f"[{message.channel_id}] {username}: {text}")
        
        # Broadcast to all subscribers in channel
        broadcast_msg = Message(
            message_id="",
            app_id=message.app_id,
            channel_id=message.channel_id,
            message_type=MessageType.PUBLISH,
            payload={
                'type': 'chat_message',
                'username': username,
                'text': text,
                'timestamp': time.time(),
                'channel': message.channel_id
            },
            timestamp=time.time()
        )
        
        app = self.server.get_application(message.app_id)
        channel = app.get_channel(message.channel_id)
        self.server._handle_publish(broadcast_msg, channel)
    
    def broadcast_user_list(self):
        user_list = [
            {
                'username': user['username'],
                'joined_at': user['joined_at']
            }
            for user in self.users.values()
        ]
        
        broadcast_msg = Message(
            message_id="",
            app_id="chat_app",
            channel_id="users",
            message_type=MessageType.PUBLISH,
            payload={
                'type': 'user_list',
                'users': user_list,
                'count': len(user_list)
            },
            timestamp=time.time()
        )
        
        app = self.server.get_application("chat_app")
        user_channel = app.get_channel("users")
        self.server._handle_publish(broadcast_msg, user_channel)
    
    def start(self):
        self.server.start()
        print("💬 Chat server started on localhost:8888")
        
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

### React Chat Client

```tsx
import React, { useState, useEffect, useRef } from 'react';
import { IPCClient } from '@ifesol/ipc-framework-js';

interface ChatMessage {
  username: string;
  text: string;
  timestamp: number;
  channel: string;
}

interface User {
  username: string;
  joined_at: number;
}

const ChatApp: React.FC = () => {
  const [client] = useState(() => new IPCClient('chat_app'));
  const [connected, setConnected] = useState(false);
  const [username, setUsername] = useState('');
  const [joined, setJoined] = useState(false);
  const [currentChannel, setCurrentChannel] = useState('general');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const channels = ['general', 'tech', 'random'];
  
  useEffect(() => {
    // Set up client event handlers
    client.onConnected(() => {
      setConnected(true);
    });
    
    client.onDisconnected(() => {
      setConnected(false);
      setJoined(false);
    });
    
    // Connect to server
    client.connect();
    
    return () => {
      if (joined) {
        client.notify('users', {
          action: 'leave',
          connection_id: client.connectionId
        });
      }
      client.disconnect();
    };
  }, [client, joined]);
  
  useEffect(() => {
    if (connected && joined) {
      // Subscribe to channels
      channels.forEach(channel => {
        client.subscribe(channel, (message) => {
          if (message.payload.type === 'chat_message') {
            setMessages(prev => [...prev, message.payload]);
          }
        });
      });
      
      // Subscribe to user updates
      client.subscribe('users', (message) => {
        if (message.payload.type === 'user_list') {
          setUsers(message.payload.users);
        }
      });
    }
  }, [client, connected, joined]);
  
  useEffect(() => {
    // Auto-scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const joinChat = async () => {
    if (!username.trim()) return;
    
    try {
      const response = await client.sendRequest('users', {
        action: 'join',
        username: username.trim(),
        connection_id: client.connectionId
      });
      
      if (response?.payload.success) {
        setJoined(true);
      }
    } catch (error) {
      console.error('Failed to join chat:', error);
    }
  };
  
  const sendMessage = () => {
    if (!newMessage.trim() || !joined) return;
    
    client.request(currentChannel, {
      text: newMessage.trim(),
      connection_id: client.connectionId
    });
    
    setNewMessage('');
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (joined) {
        sendMessage();
      } else {
        joinChat();
      }
    }
  };
  
  if (!connected) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-xl mb-4">🔄 Connecting to chat server...</div>
          <div className="text-gray-500">Make sure the Python server is running</div>
        </div>
      </div>
    );
  }
  
  if (!joined) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-md w-96">
          <h1 className="text-2xl font-bold mb-6 text-center">Join Chat</h1>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your username"
            className="w-full p-3 border border-gray-300 rounded-lg mb-4"
            autoFocus
          />
          <button
            onClick={joinChat}
            disabled={!username.trim()}
            className="w-full bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
          >
            Join Chat
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-md">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Chat Channels</h2>
        </div>
        
        <div className="p-2">
          {channels.map(channel => (
            <button
              key={channel}
              onClick={() => setCurrentChannel(channel)}
              className={`w-full text-left p-3 rounded-lg mb-1 hover:bg-gray-100 ${
                currentChannel === channel ? 'bg-blue-100 text-blue-600' : ''
              }`}
            >
              # {channel}
            </button>
          ))}
        </div>
        
        <div className="p-4 border-t mt-4">
          <h3 className="text-sm font-semibold mb-2">Online Users ({users.length})</h3>
          <div className="space-y-1">
            {users.map((user, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm">{user.username}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white p-4 border-b shadow-sm">
          <h1 className="text-xl font-semibold">#{currentChannel}</h1>
          <p className="text-sm text-gray-500">Welcome, {username}!</p>
        </div>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages
            .filter(msg => msg.channel === currentChannel)
            .map((msg, index) => (
            <div key={index} className="flex space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                {msg.username[0].toUpperCase()}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold">{msg.username}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(msg.timestamp * 1000).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-gray-800">{msg.text}</p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Message Input */}
        <div className="bg-white border-t p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message #${currentChannel}`}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={sendMessage}
              disabled={!newMessage.trim()}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatApp;
```

## API Server

### Python API Backend

```python
from ipc_framework import FrameworkServer, MessageType
import json
import time
import uuid

class APIServer:
    def __init__(self):
        self.server = FrameworkServer(host="localhost", port=8888)
        self.data_store = {
            'users': [
                {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
                {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
            ],
            'posts': [
                {'id': 1, 'title': 'Hello World', 'content': 'First post', 'user_id': 1},
                {'id': 2, 'title': 'Python is Great', 'content': 'Love coding in Python', 'user_id': 2}
            ]
        }
        self.setup_api()
    
    def setup_api(self):
        app = self.server.create_application("api_app", "API Application")
        
        # REST-like API endpoints
        api_channel = app.create_channel("api")
        api_channel.set_handler(MessageType.REQUEST, self.handle_api_request)
        
        # Real-time updates channel
        updates_channel = app.create_channel("updates")
    
    def handle_api_request(self, message):
        try:
            endpoint = message.payload.get('endpoint')
            method = message.payload.get('method', 'GET')
            data = message.payload.get('data', {})
            
            response_data = self.route_api_call(endpoint, method, data)
            
        except Exception as e:
            response_data = {
                'error': True,
                'message': str(e),
                'status': 500
            }
        
        # Send response
        response = message.create_response(response_data)
        connection = self.server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        if connection:
            self.server.send_to_connection(connection, response)
    
    def route_api_call(self, endpoint, method, data):
        if endpoint == '/users':
            if method == 'GET':
                return {'users': self.data_store['users'], 'status': 200}
            elif method == 'POST':
                new_user = {
                    'id': len(self.data_store['users']) + 1,
                    'name': data.get('name'),
                    'email': data.get('email')
                }
                self.data_store['users'].append(new_user)
                self.broadcast_update('user_created', new_user)
                return {'user': new_user, 'status': 201}
        
        elif endpoint.startswith('/users/'):
            user_id = int(endpoint.split('/')[-1])
            user = next((u for u in self.data_store['users'] if u['id'] == user_id), None)
            
            if method == 'GET':
                if user:
                    return {'user': user, 'status': 200}
                else:
                    return {'error': 'User not found', 'status': 404}
            
            elif method == 'PUT':
                if user:
                    user.update(data)
                    self.broadcast_update('user_updated', user)
                    return {'user': user, 'status': 200}
                else:
                    return {'error': 'User not found', 'status': 404}
        
        elif endpoint == '/posts':
            if method == 'GET':
                return {'posts': self.data_store['posts'], 'status': 200}
            elif method == 'POST':
                new_post = {
                    'id': len(self.data_store['posts']) + 1,
                    'title': data.get('title'),
                    'content': data.get('content'),
                    'user_id': data.get('user_id')
                }
                self.data_store['posts'].append(new_post)
                self.broadcast_update('post_created', new_post)
                return {'post': new_post, 'status': 201}
        
        else:
            return {'error': 'Endpoint not found', 'status': 404}
    
    def broadcast_update(self, event_type, data):
        """Broadcast real-time updates to subscribers"""
        from ipc_framework import Message
        
        update_msg = Message(
            message_id="",
            app_id="api_app",
            channel_id="updates",
            message_type=MessageType.PUBLISH,
            payload={
                'type': event_type,
                'data': data,
                'timestamp': time.time()
            },
            timestamp=time.time()
        )
        
        app = self.server.get_application("api_app")
        updates_channel = app.get_channel("updates")
        self.server._handle_publish(update_msg, updates_channel)
    
    def start(self):
        self.server.start()
        print("🌐 API server started on localhost:8888")
        print("Available endpoints:")
        print("  GET    /users")
        print("  POST   /users")
        print("  GET    /users/:id")
        print("  PUT    /users/:id")
        print("  GET    /posts")
        print("  POST   /posts")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.server.stop()
            print("API server stopped")

if __name__ == "__main__":
    api_server = APIServer()
    api_server.start()
```

### JavaScript API Client

```typescript
import { IPCClient } from '@ifesol/ipc-framework-js';

class APIClient {
  private client: IPCClient;
  private updateHandlers: Map<string, Function[]> = new Map();
  
  constructor() {
    this.client = new IPCClient('api_app');
    this.setupEventHandlers();
  }
  
  private setupEventHandlers(): void {
    this.client.onConnected(() => {
      console.log('🌐 Connected to API server');
      
      // Subscribe to real-time updates
      this.client.subscribe('updates', (message) => {
        const { type, data } = message.payload;
        const handlers = this.updateHandlers.get(type) || [];
        handlers.forEach(handler => handler(data));
      });
    });
  }
  
  async connect(): Promise<boolean> {
    return await this.client.connect();
  }
  
  // REST-like methods
  async get(endpoint: string): Promise<any> {
    const response = await this.client.sendRequest('api', {
      endpoint,
      method: 'GET',
      connection_id: this.client.connectionId
    });
    
    return response?.payload;
  }
  
  async post(endpoint: string, data: any): Promise<any> {
    const response = await this.client.sendRequest('api', {
      endpoint,
      method: 'POST',
      data,
      connection_id: this.client.connectionId
    });
    
    return response?.payload;
  }
  
  async put(endpoint: string, data: any): Promise<any> {
    const response = await this.client.sendRequest('api', {
      endpoint,
      method: 'PUT',
      data,
      connection_id: this.client.connectionId
    });
    
    return response?.payload;
  }
  
  // Real-time update subscriptions
  onUpdate(eventType: string, handler: (data: any) => void): void {
    if (!this.updateHandlers.has(eventType)) {
      this.updateHandlers.set(eventType, []);
    }
    this.updateHandlers.get(eventType)!.push(handler);
  }
  
  // Convenience methods
  async getUsers(): Promise<any[]> {
    const result = await this.get('/users');
    return result?.users || [];
  }
  
  async createUser(name: string, email: string): Promise<any> {
    return await this.post('/users', { name, email });
  }
  
  async getUser(id: number): Promise<any> {
    const result = await this.get(`/users/${id}`);
    return result?.user;
  }
  
  async updateUser(id: number, data: any): Promise<any> {
    return await this.put(`/users/${id}`, data);
  }
  
  async getPosts(): Promise<any[]> {
    const result = await this.get('/posts');
    return result?.posts || [];
  }
  
  async createPost(title: string, content: string, userId: number): Promise<any> {
    return await this.post('/posts', { title, content, user_id: userId });
  }
  
  disconnect(): void {
    this.client.disconnect();
  }
}

// Usage example
async function main() {
  const api = new APIClient();
  
  // Set up real-time update handlers
  api.onUpdate('user_created', (user) => {
    console.log('🆕 New user created:', user);
  });
  
  api.onUpdate('post_created', (post) => {
    console.log('📝 New post created:', post);
  });
  
  // Connect to API
  await api.connect();
  
  try {
    // Get all users
    const users = await api.getUsers();
    console.log('👥 Users:', users);
    
    // Create a new user
    const newUser = await api.createUser('Bob Wilson', 'bob@example.com');
    console.log('✅ Created user:', newUser);
    
    // Get all posts
    const posts = await api.getPosts();
    console.log('📚 Posts:', posts);
    
    // Create a new post
    const newPost = await api.createPost(
      'JavaScript is Awesome',
      'I love working with the IPC framework!',
      newUser.user.id
    );
    console.log('✅ Created post:', newPost);
    
  } catch (error) {
    console.error('❌ API error:', error);
  }
  
  // Keep connection alive for real-time updates
  setTimeout(() => {
    api.disconnect();
  }, 30000); // Disconnect after 30 seconds
}

main();
```

**Run the API example:**
```bash
# Terminal 1: Start Python API server
python api_server.py

# Terminal 2: Run JavaScript API client
node api_client.js
```

This demonstrates a complete REST-like API with real-time updates, showing how Python and JavaScript can work together seamlessly using the IPC framework! 