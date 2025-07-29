# Integration Guide - IPC Framework

This guide shows how to integrate both packages for real-world applications.

## 🚨 **Critical: Version 1.1.0 Required**

**Before integrating, ensure you have the working version:**
```bash
pip install --upgrade ipc-framework  # Must be v1.1.0+
```

**v1.0.0 integration will fail due to critical bugs. Only v1.1.0+ provides reliable integration.**

## Table of Contents

- [Python Backend + React Frontend](#python-backend--react-frontend)
- [Python Backend + Vue.js Frontend](#python-backend--vuejs-frontend)
- [Python Backend + Angular Frontend](#python-backend--angular-frontend)
- [Python Backend + Node.js Service](#python-backend--nodejs-service)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)

## Python Backend + React Frontend

### Project Structure
```
my-app/
├── backend/
│   ├── requirements.txt
│   ├── server.py
│   └── api/
│       ├── __init__.py
│       ├── users.py
│       └── chat.py
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── hooks/
│   │   │   └── useIPC.ts
│   │   ├── components/
│   │   │   ├── Chat.tsx
│   │   │   └── UserList.tsx
│   │   └── App.tsx
│   └── public/
└── docker-compose.yml
```

### Backend Setup

**requirements.txt:**
```
ipc-framework
uvloop  # For better performance
```

**server.py:**
```python
from ipc_framework import FrameworkServer, MessageType
import asyncio
import uvloop
import json
from api.users import UserManager
from api.chat import ChatManager

class AppServer:
    def __init__(self):
        self.server = FrameworkServer(host="0.0.0.0", port=8888)
        self.user_manager = UserManager()
        self.chat_manager = ChatManager()
        self.setup_applications()
    
    def setup_applications(self):
        # User Management App
        user_app = self.server.create_application("user_app", "User Management")
        auth_channel = user_app.create_channel("auth")
        profile_channel = user_app.create_channel("profile")
        
        auth_channel.set_handler(MessageType.REQUEST, self.handle_auth)
        profile_channel.set_handler(MessageType.REQUEST, self.handle_profile)
        
        # Chat App
        chat_app = self.server.create_application("chat_app", "Chat System")
        chat_channel = chat_app.create_channel("messages")
        rooms_channel = chat_app.create_channel("rooms")
        
        chat_channel.set_handler(MessageType.REQUEST, self.handle_chat_message)
        rooms_channel.set_handler(MessageType.REQUEST, self.handle_room_action)
        
        # Real-time notifications
        notifications_app = self.server.create_application("notifications", "Notifications")
        alerts_channel = notifications_app.create_channel("alerts")
    
    def handle_auth(self, message):
        action = message.payload.get('action')
        
        if action == 'login':
            result = self.user_manager.login(
                message.payload.get('username'),
                message.payload.get('password')
            )
        elif action == 'register':
            result = self.user_manager.register(
                message.payload.get('username'),
                message.payload.get('email'),
                message.payload.get('password')
            )
        else:
            result = {'error': 'Unknown action'}
        
        response = message.create_response(result)
        connection = self.server.connection_manager.get_connection(
            message.payload.get('connection_id')
        )
        if connection:
            self.server.send_to_connection(connection, response)
    
    def handle_chat_message(self, message):
        result = self.chat_manager.send_message(
            message.payload.get('room_id'),
            message.payload.get('user_id'),
            message.payload.get('text')
        )
        
        if result.get('success'):
            # Broadcast to all users in room
            self.broadcast_to_room(result['room_id'], {
                'type': 'new_message',
                'message': result['message']
            })
    
    def broadcast_to_room(self, room_id, data):
        # Implementation for broadcasting to room members
        pass
    
    def start(self):
        # Use uvloop for better performance
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
        self.server.start()
        print("🚀 Backend server running on port 8888")
        
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            self.server.stop()

if __name__ == "__main__":
    server = AppServer()
    server.start()
```

### Frontend Setup

**package.json:**
```json
{
  "name": "ipc-react-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@ifesol/ipc-framework-js": "^1.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
```

**src/hooks/useIPC.ts:**
```typescript
import { useState, useEffect, useRef, useCallback } from 'react';
import { IPCClient, Message } from '@ifesol/ipc-framework-js';

interface UseIPCOptions {
  autoConnect?: boolean;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: Error) => void;
}

export const useIPC = (appId: string, options: UseIPCOptions = {}) => {
  const clientRef = useRef<IPCClient>();
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [reconnecting, setReconnecting] = useState(false);
  
  const { autoConnect = true, onConnected, onDisconnected, onError } = options;
  
  useEffect(() => {
    if (!clientRef.current) {
      clientRef.current = new IPCClient(appId, {
        host: process.env.REACT_APP_IPC_HOST || 'localhost',
        port: parseInt(process.env.REACT_APP_IPC_PORT || '8888'),
        reconnectAttempts: 10,
        reconnectDelay: 1000
      });
      
      clientRef.current.onConnected(() => {
        setConnected(true);
        setError(null);
        setReconnecting(false);
        onConnected?.();
      });
      
      clientRef.current.onDisconnected(() => {
        setConnected(false);
        setReconnecting(true);
        onDisconnected?.();
      });
      
      clientRef.current.onError((err) => {
        setError(err);
        onError?.(err);
      });
    }
    
    if (autoConnect && clientRef.current && !connected) {
      clientRef.current.connect();
    }
    
    return () => {
      if (clientRef.current) {
        clientRef.current.disconnect();
      }
    };
  }, [appId, autoConnect, connected, onConnected, onDisconnected, onError]);
  
  const connect = useCallback(async () => {
    if (clientRef.current) {
      return await clientRef.current.connect();
    }
    return false;
  }, []);
  
  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
    }
  }, []);
  
  const sendRequest = useCallback(async (channelId: string, data: any, timeout?: number) => {
    if (clientRef.current && connected) {
      return await clientRef.current.sendRequest(channelId, {
        ...data,
        connection_id: clientRef.current.connectionId
      }, timeout);
    }
    return null;
  }, [connected]);
  
  const subscribe = useCallback((channelId: string, handler: (message: Message) => void) => {
    if (clientRef.current) {
      return clientRef.current.subscribe(channelId, handler);
    }
    return false;
  }, []);
  
  const notify = useCallback((channelId: string, data: any) => {
    if (clientRef.current && connected) {
      return clientRef.current.notify(channelId, {
        ...data,
        connection_id: clientRef.current.connectionId
      });
    }
    return '';
  }, [connected]);
  
  return {
    client: clientRef.current,
    connected,
    error,
    reconnecting,
    connect,
    disconnect,
    sendRequest,
    subscribe,
    notify
  };
};

export const useAuth = () => {
  const { sendRequest, connected } = useIPC('user_app');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await sendRequest('auth', {
        action: 'login',
        username,
        password
      });
      
      if (response?.payload.success) {
        setUser(response.payload.user);
        localStorage.setItem('user', JSON.stringify(response.payload.user));
        return { success: true };
      } else {
        return { success: false, error: response?.payload.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    } finally {
      setLoading(false);
    }
  };
  
  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };
  
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);
  
  return { user, login, logout, loading, connected };
};
```

**src/components/Chat.tsx:**
```tsx
import React, { useState, useEffect, useRef } from 'react';
import { useIPC } from '../hooks/useIPC';

interface ChatMessage {
  id: string;
  user_id: string;
  username: string;
  text: string;
  timestamp: number;
  room_id: string;
}

interface ChatProps {
  user: any;
  roomId: string;
}

export const Chat: React.FC<ChatProps> = ({ user, roomId }) => {
  const { sendRequest, subscribe, connected } = useIPC('chat_app');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (connected) {
      // Subscribe to new messages
      subscribe('messages', (message) => {
        if (message.payload.type === 'new_message') {
          const newMsg = message.payload.message;
          if (newMsg.room_id === roomId) {
            setMessages(prev => [...prev, newMsg]);
          }
        }
      });
      
      // Load existing messages
      loadMessages();
    }
  }, [connected, roomId, subscribe]);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const loadMessages = async () => {
    setLoading(true);
    try {
      const response = await sendRequest('messages', {
        action: 'get_messages',
        room_id: roomId,
        limit: 50
      });
      
      if (response?.payload.success) {
        setMessages(response.payload.messages);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const sendMessage = async () => {
    if (!newMessage.trim() || !connected) return;
    
    try {
      await sendRequest('messages', {
        action: 'send_message',
        room_id: roomId,
        user_id: user.id,
        text: newMessage.trim()
      });
      
      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  if (loading) {
    return <div className="flex justify-center p-4">Loading messages...</div>;
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.user_id === user.id ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                message.user_id === user.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              {message.user_id !== user.id && (
                <div className="text-xs font-semibold mb-1">{message.username}</div>
              )}
              <div>{message.text}</div>
              <div className="text-xs opacity-70 mt-1">
                {new Date(message.timestamp * 1000).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Message Input */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 resize-none border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={1}
            disabled={!connected}
          />
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim() || !connected}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
          >
            Send
          </button>
        </div>
        {!connected && (
          <div className="text-red-500 text-sm mt-2">
            Disconnected from server. Attempting to reconnect...
          </div>
        )}
      </div>
    </div>
  );
};
```

**src/App.tsx:**
```tsx
import React from 'react';
import { useAuth } from './hooks/useIPC';
import { Chat } from './components/Chat';
import { Login } from './components/Login';

const App: React.FC = () => {
  const { user, connected } = useAuth();
  
  if (!connected) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-xl mb-4">🔄 Connecting to server...</div>
          <div className="text-gray-500">
            Make sure the backend server is running on port 8888
          </div>
        </div>
      </div>
    );
  }
  
  if (!user) {
    return <Login />;
  }
  
  return (
    <div className="h-screen bg-gray-50">
      <div className="h-full max-w-4xl mx-auto bg-white shadow-lg">
        <Chat user={user} roomId="general" />
      </div>
    </div>
  );
};

export default App;
```

### Development Workflow

**Start Backend:**
```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Start Frontend:**
```bash
cd frontend
npm install
npm start
```

### Environment Configuration

**.env (Frontend):**
```
REACT_APP_IPC_HOST=localhost
REACT_APP_IPC_PORT=8888
```

**config.py (Backend):**
```python
import os

class Config:
    IPC_HOST = os.getenv('IPC_HOST', 'localhost')
    IPC_PORT = int(os.getenv('IPC_PORT', '8888'))
    MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '1000'))
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    IPC_HOST = '0.0.0.0'
```

## Python Backend + Vue.js Frontend

### Vue Composable

**composables/useIPC.ts:**
```typescript
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { IPCClient, Message } from '@ifesol/ipc-framework-js';

export function useIPC(appId: string, options: any = {}) {
  const client = ref<IPCClient>();
  const connected = ref(false);
  const error = ref<Error | null>(null);
  const reconnecting = ref(false);
  
  onMounted(async () => {
    client.value = new IPCClient(appId, {
      host: import.meta.env.VITE_IPC_HOST || 'localhost',
      port: parseInt(import.meta.env.VITE_IPC_PORT || '8888'),
      ...options
    });
    
    client.value.onConnected(() => {
      connected.value = true;
      error.value = null;
      reconnecting.value = false;
    });
    
    client.value.onDisconnected(() => {
      connected.value = false;
      reconnecting.value = true;
    });
    
    client.value.onError((err) => {
      error.value = err;
    });
    
    await client.value.connect();
  });
  
  onUnmounted(() => {
    client.value?.disconnect();
  });
  
  const sendRequest = async (channelId: string, data: any, timeout?: number) => {
    if (client.value && connected.value) {
      return await client.value.sendRequest(channelId, {
        ...data,
        connection_id: client.value.connectionId
      }, timeout);
    }
    return null;
  };
  
  const subscribe = (channelId: string, handler: (message: Message) => void) => {
    return client.value?.subscribe(channelId, handler) || false;
  };
  
  return {
    client: computed(() => client.value),
    connected: computed(() => connected.value),
    error: computed(() => error.value),
    reconnecting: computed(() => reconnecting.value),
    sendRequest,
    subscribe
  };
}
```

### Vue Component

**components/ChatRoom.vue:**
```vue
<template>
  <div class="chat-room h-full flex flex-col">
    <!-- Connection Status -->
    <div v-if="!connected" class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm">
            {{ reconnecting ? 'Reconnecting to server...' : 'Disconnected from server' }}
          </p>
        </div>
      </div>
    </div>
    
    <!-- Messages Area -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 bg-gray-50">
      <div v-for="message in messages" :key="message.id" class="mb-4">
        <div :class="['flex', message.user_id === currentUser?.id ? 'justify-end' : 'justify-start']">
          <div :class="[
            'max-w-xs lg:max-w-md px-4 py-2 rounded-lg',
            message.user_id === currentUser?.id 
              ? 'bg-blue-500 text-white' 
              : 'bg-white shadow'
          ]">
            <div v-if="message.user_id !== currentUser?.id" class="text-xs font-semibold mb-1 text-gray-600">
              {{ message.username }}
            </div>
            <p class="text-sm">{{ message.text }}</p>
            <div class="text-xs mt-1 opacity-70">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Message Input -->
    <div class="border-t bg-white p-4">
      <div class="flex space-x-2">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          :disabled="!connected"
          type="text"
          placeholder="Type your message..."
          class="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          @click="sendMessage"
          :disabled="!newMessage.trim() || !connected"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue';
import { useIPC } from '../composables/useIPC';
import { useAuth } from '../composables/useAuth';

interface ChatMessage {
  id: string;
  user_id: string;
  username: string;
  text: string;
  timestamp: number;
  room_id: string;
}

const props = defineProps<{
  roomId: string;
}>();

const { currentUser } = useAuth();
const { connected, reconnecting, sendRequest, subscribe } = useIPC('chat_app');

const messages = ref<ChatMessage[]>([]);
const newMessage = ref('');
const messagesContainer = ref<HTMLElement>();

onMounted(() => {
  if (connected.value) {
    setupChat();
  } else {
    // Watch for connection
    const unwatch = computed(() => connected.value).effect(() => {
      if (connected.value) {
        setupChat();
        unwatch();
      }
    });
  }
});

const setupChat = () => {
  // Subscribe to new messages
  subscribe('messages', (message) => {
    if (message.payload.type === 'new_message') {
      const newMsg = message.payload.message;
      if (newMsg.room_id === props.roomId) {
        messages.value.push(newMsg);
        scrollToBottom();
      }
    }
  });
  
  // Load existing messages
  loadMessages();
};

const loadMessages = async () => {
  try {
    const response = await sendRequest('messages', {
      action: 'get_messages',
      room_id: props.roomId,
      limit: 50
    });
    
    if (response?.payload.success) {
      messages.value = response.payload.messages;
      await nextTick();
      scrollToBottom();
    }
  } catch (error) {
    console.error('Failed to load messages:', error);
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim() || !connected.value || !currentUser.value) return;
  
  try {
    await sendRequest('messages', {
      action: 'send_message',
      room_id: props.roomId,
      user_id: currentUser.value.id,
      text: newMessage.value.trim()
    });
    
    newMessage.value = '';
  } catch (error) {
    console.error('Failed to send message:', error);
  }
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const formatTime = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleTimeString();
};
</script>
```

## Python Backend + Angular Frontend

### Angular Service

**services/ipc.service.ts:**
```typescript
import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { IPCClient, Message } from '@ifesol/ipc-framework-js';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class IPCService implements OnDestroy {
  private clients: Map<string, IPCClient> = new Map();
  private connectionStates: Map<string, BehaviorSubject<boolean>> = new Map();
  private messageSubjects: Map<string, Subject<Message>> = new Map();
  
  constructor() {}
  
  async connect(appId: string): Promise<boolean> {
    if (this.clients.has(appId)) {
      return this.clients.get(appId)!.isConnected();
    }
    
    const client = new IPCClient(appId, {
      host: environment.ipcHost,
      port: environment.ipcPort,
      reconnectAttempts: 10
    });
    
    const connectionState = new BehaviorSubject<boolean>(false);
    
    client.onConnected(() => {
      connectionState.next(true);
    });
    
    client.onDisconnected(() => {
      connectionState.next(false);
    });
    
    this.clients.set(appId, client);
    this.connectionStates.set(appId, connectionState);
    
    return await client.connect();
  }
  
  getConnectionState(appId: string): Observable<boolean> {
    const state = this.connectionStates.get(appId);
    return state ? state.asObservable() : new BehaviorSubject(false).asObservable();
  }
  
  subscribeToChannel(appId: string, channelId: string): Observable<Message> {
    const key = `${appId}:${channelId}`;
    
    if (!this.messageSubjects.has(key)) {
      const subject = new Subject<Message>();
      this.messageSubjects.set(key, subject);
      
      const client = this.clients.get(appId);
      if (client) {
        client.subscribe(channelId, (message) => {
          subject.next(message);
        });
      }
    }
    
    return this.messageSubjects.get(key)!.asObservable();
  }
  
  async sendRequest(appId: string, channelId: string, data: any, timeout?: number): Promise<any> {
    const client = this.clients.get(appId);
    if (client && client.isConnected()) {
      const response = await client.sendRequest(channelId, {
        ...data,
        connection_id: client.connectionId
      }, timeout);
      return response?.payload;
    }
    throw new Error(`Client for app ${appId} not connected`);
  }
  
  sendNotification(appId: string, channelId: string, data: any): void {
    const client = this.clients.get(appId);
    if (client && client.isConnected()) {
      client.notify(channelId, {
        ...data,
        connection_id: client.connectionId
      });
    }
  }
  
  ngOnDestroy(): void {
    // Cleanup all clients
    this.clients.forEach(client => client.disconnect());
    this.clients.clear();
    this.connectionStates.clear();
    this.messageSubjects.forEach(subject => subject.complete());
    this.messageSubjects.clear();
  }
}
```

### Angular Component

**components/chat/chat.component.ts:**
```typescript
import { Component, OnInit, OnDestroy, ElementRef, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Subscription } from 'rxjs';
import { IPCService } from '../../services/ipc.service';
import { AuthService } from '../../services/auth.service';

interface ChatMessage {
  id: string;
  user_id: string;
  username: string;
  text: string;
  timestamp: number;
  room_id: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;
  
  messages: ChatMessage[] = [];
  messageControl = new FormControl('');
  connected = false;
  currentUser: any = null;
  roomId = 'general';
  
  private subscriptions: Subscription[] = [];
  
  constructor(
    private ipcService: IPCService,
    private authService: AuthService
  ) {}
  
  async ngOnInit() {
    this.currentUser = this.authService.getCurrentUser();
    
    // Connect to chat app
    await this.ipcService.connect('chat_app');
    
    // Subscribe to connection state
    const connectionSub = this.ipcService.getConnectionState('chat_app').subscribe(
      connected => {
        this.connected = connected;
        if (connected) {
          this.setupChat();
        }
      }
    );
    this.subscriptions.push(connectionSub);
  }
  
  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
  
  private setupChat() {
    // Subscribe to chat messages
    const messagesSub = this.ipcService.subscribeToChannel('chat_app', 'messages').subscribe(
      message => {
        if (message.payload.type === 'new_message') {
          const newMsg = message.payload.message;
          if (newMsg.room_id === this.roomId) {
            this.messages.push(newMsg);
            this.scrollToBottom();
          }
        }
      }
    );
    this.subscriptions.push(messagesSub);
    
    // Load existing messages
    this.loadMessages();
  }
  
  private async loadMessages() {
    try {
      const response = await this.ipcService.sendRequest('chat_app', 'messages', {
        action: 'get_messages',
        room_id: this.roomId,
        limit: 50
      });
      
      if (response.success) {
        this.messages = response.messages;
        setTimeout(() => this.scrollToBottom(), 100);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  }
  
  async sendMessage() {
    const text = this.messageControl.value?.trim();
    if (!text || !this.connected || !this.currentUser) return;
    
    try {
      await this.ipcService.sendRequest('chat_app', 'messages', {
        action: 'send_message',
        room_id: this.roomId,
        user_id: this.currentUser.id,
        text: text
      });
      
      this.messageControl.setValue('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }
  
  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
  
  private scrollToBottom() {
    if (this.messagesContainer) {
      const element = this.messagesContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    }
  }
  
  isOwnMessage(message: ChatMessage): boolean {
    return message.user_id === this.currentUser?.id;
  }
  
  formatTime(timestamp: number): string {
    return new Date(timestamp * 1000).toLocaleTimeString();
  }
}
```

## Production Deployment

### Docker Setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8888:8888"
    environment:
      - IPC_HOST=0.0.0.0
      - IPC_PORT=8888
      - MAX_CONNECTIONS=1000
    volumes:
      - ./backend:/app
    restart: unless-stopped
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_IPC_HOST=localhost
      - REACT_APP_IPC_PORT=8888
    depends_on:
      - backend
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

**backend/Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

CMD ["python", "server.py"]
```

**frontend/Dockerfile:**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

**nginx.conf:**
```nginx
upstream backend {
    server backend:8888;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket API
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Production Environment Variables

**backend/.env.production:**
```
IPC_HOST=0.0.0.0
IPC_PORT=8888
MAX_CONNECTIONS=5000
LOG_LEVEL=INFO
```

**frontend/.env.production:**
```
REACT_APP_IPC_HOST=your-domain.com
REACT_APP_IPC_PORT=8888
REACT_APP_API_URL=https://your-domain.com
```

This comprehensive integration guide shows how to build production-ready applications using both IPC Framework packages together! 🚀 