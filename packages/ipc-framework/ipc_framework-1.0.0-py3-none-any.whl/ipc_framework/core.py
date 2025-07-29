"""
Core classes for the IPC Framework
"""

import json
import uuid
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum


class MessageType(Enum):
    """Types of messages in the IPC system"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PUBLISH = "publish"


@dataclass
class Message:
    """Represents a message in the IPC system"""
    message_id: str
    app_id: str
    channel_id: str
    message_type: MessageType
    payload: Any
    timestamp: float
    reply_to: Optional[str] = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary for serialization"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create message from dictionary"""
        data['message_type'] = MessageType(data['message_type'])
        return cls(**data)
    
    def to_json(self) -> str:
        """Serialize message to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserialize message from JSON"""
        return cls.from_dict(json.loads(json_str))


class Channel:
    """Represents a communication channel within an application"""
    
    def __init__(self, channel_id: str, app_id: str):
        self.channel_id = channel_id
        self.app_id = app_id
        self.subscribers: List[str] = []  # Connection IDs
        self.handlers: Dict[MessageType, Callable] = {}
        self.created_at = time.time()
        self._lock = threading.RLock()
    
    def add_subscriber(self, connection_id: str):
        """Add a subscriber to this channel"""
        with self._lock:
            if connection_id not in self.subscribers:
                self.subscribers.append(connection_id)
    
    def remove_subscriber(self, connection_id: str):
        """Remove a subscriber from this channel"""
        with self._lock:
            if connection_id in self.subscribers:
                self.subscribers.remove(connection_id)
    
    def set_handler(self, message_type: MessageType, handler: Callable):
        """Set a message handler for this channel"""
        with self._lock:
            self.handlers[message_type] = handler
    
    def get_handler(self, message_type: MessageType) -> Optional[Callable]:
        """Get the handler for a message type"""
        with self._lock:
            return self.handlers.get(message_type)
    
    def get_subscribers(self) -> List[str]:
        """Get list of current subscribers"""
        with self._lock:
            return self.subscribers.copy()


class Application:
    """Represents an application with multiple channels"""
    
    def __init__(self, app_id: str, name: str = None):
        self.app_id = app_id
        self.name = name or app_id
        self.channels: Dict[str, Channel] = {}
        self.created_at = time.time()
        self.last_activity = time.time()
        self._lock = threading.RLock()
    
    def create_channel(self, channel_id: str) -> Channel:
        """Create a new channel in this application"""
        with self._lock:
            if channel_id in self.channels:
                return self.channels[channel_id]
            
            channel = Channel(channel_id, self.app_id)
            self.channels[channel_id] = channel
            self.last_activity = time.time()
            return channel
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel by ID"""
        with self._lock:
            return self.channels.get(channel_id)
    
    def remove_channel(self, channel_id: str) -> bool:
        """Remove a channel"""
        with self._lock:
            if channel_id in self.channels:
                del self.channels[channel_id]
                self.last_activity = time.time()
                return True
            return False
    
    def list_channels(self) -> List[str]:
        """List all channel IDs in this application"""
        with self._lock:
            return list(self.channels.keys())
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = time.time()


class ConnectionManager:
    """Manages client connections"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}  # connection_id -> connection object
        self.connection_apps: Dict[str, str] = {}  # connection_id -> app_id
        self._lock = threading.RLock()
    
    def add_connection(self, connection_id: str, connection_obj: Any, app_id: str):
        """Add a new connection"""
        with self._lock:
            self.connections[connection_id] = connection_obj
            self.connection_apps[connection_id] = app_id
    
    def remove_connection(self, connection_id: str):
        """Remove a connection"""
        with self._lock:
            self.connections.pop(connection_id, None)
            self.connection_apps.pop(connection_id, None)
    
    def get_connection(self, connection_id: str) -> Optional[Any]:
        """Get a connection object"""
        with self._lock:
            return self.connections.get(connection_id)
    
    def get_connections_for_app(self, app_id: str) -> List[str]:
        """Get all connection IDs for an application"""
        with self._lock:
            return [conn_id for conn_id, app in self.connection_apps.items() if app == app_id]
    
    def list_connections(self) -> List[str]:
        """List all connection IDs"""
        with self._lock:
            return list(self.connections.keys())


class IPCServer:
    """Base IPC Server class"""
    
    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.applications: Dict[str, Application] = {}
        self.connection_manager = ConnectionManager()
        self.running = False
        self._lock = threading.RLock()
    
    def create_application(self, app_id: str, name: str = None) -> Application:
        """Create a new application"""
        with self._lock:
            if app_id in self.applications:
                return self.applications[app_id]
            
            app = Application(app_id, name)
            self.applications[app_id] = app
            return app
    
    def get_application(self, app_id: str) -> Optional[Application]:
        """Get an application by ID"""
        with self._lock:
            return self.applications.get(app_id)
    
    def route_message(self, message: Message) -> bool:
        """Route a message to the appropriate handlers"""
        with self._lock:
            app = self.get_application(message.app_id)
            if not app:
                return False
            
            channel = app.get_channel(message.channel_id)
            if not channel:
                return False
            
            app.update_activity()
            
            # Handle different message types
            if message.message_type == MessageType.PUBLISH:
                return self._handle_publish(message, channel)
            elif message.message_type == MessageType.SUBSCRIBE:
                return self._handle_subscribe(message, channel)
            elif message.message_type == MessageType.UNSUBSCRIBE:
                return self._handle_unsubscribe(message, channel)
            else:
                handler = channel.get_handler(message.message_type)
                if handler:
                    try:
                        handler(message)
                        return True
                    except Exception as e:
                        print(f"Handler error: {e}")
                        return False
            
            return False
    
    def _handle_publish(self, message: Message, channel: Channel) -> bool:
        """Handle publish message by broadcasting to subscribers"""
        subscribers = channel.get_subscribers()
        for subscriber_id in subscribers:
            connection = self.connection_manager.get_connection(subscriber_id)
            if connection:
                self.send_to_connection(connection, message)
        return True
    
    def _handle_subscribe(self, message: Message, channel: Channel) -> bool:
        """Handle subscribe message"""
        # Extract connection ID from message payload
        connection_id = message.payload.get('connection_id')
        if connection_id:
            channel.add_subscriber(connection_id)
            return True
        return False
    
    def _handle_unsubscribe(self, message: Message, channel: Channel) -> bool:
        """Handle unsubscribe message"""
        connection_id = message.payload.get('connection_id')
        if connection_id:
            channel.remove_subscriber(connection_id)
            return True
        return False
    
    def send_to_connection(self, connection, message: Message):
        """Send message to a specific connection - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement send_to_connection")
    
    def start(self):
        """Start the server - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement start")
    
    def stop(self):
        """Stop the server - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement stop")


class IPCClient:
    """Base IPC Client class"""
    
    def __init__(self, app_id: str, host: str = "localhost", port: int = 8888):
        self.app_id = app_id
        self.host = host
        self.port = port
        self.connection_id = str(uuid.uuid4())
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}  # channel_id -> handler
        self._lock = threading.RLock()
    
    def connect(self) -> bool:
        """Connect to the server - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement connect")
    
    def disconnect(self):
        """Disconnect from the server - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement disconnect")
    
    def send_message(self, channel_id: str, message_type: MessageType, payload: Any, reply_to: str = None) -> str:
        """Send a message to a specific channel"""
        message = Message(
            message_id=str(uuid.uuid4()),
            app_id=self.app_id,
            channel_id=channel_id,
            message_type=message_type,
            payload=payload,
            timestamp=time.time(),
            reply_to=reply_to
        )
        return self._send_message(message)
    
    def _send_message(self, message: Message) -> str:
        """Internal method to send message - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _send_message")
    
    def subscribe(self, channel_id: str, handler: Callable = None) -> bool:
        """Subscribe to a channel"""
        if handler:
            with self._lock:
                self.message_handlers[channel_id] = handler
        
        payload = {'connection_id': self.connection_id}
        self.send_message(channel_id, MessageType.SUBSCRIBE, payload)
        return True
    
    def unsubscribe(self, channel_id: str) -> bool:
        """Unsubscribe from a channel"""
        with self._lock:
            self.message_handlers.pop(channel_id, None)
        
        payload = {'connection_id': self.connection_id}
        self.send_message(channel_id, MessageType.UNSUBSCRIBE, payload)
        return True
    
    def publish(self, channel_id: str, data: Any) -> str:
        """Publish data to a channel"""
        return self.send_message(channel_id, MessageType.PUBLISH, data)
    
    def request(self, channel_id: str, data: Any) -> str:
        """Send a request message"""
        return self.send_message(channel_id, MessageType.REQUEST, data)
    
    def handle_message(self, message: Message):
        """Handle incoming message"""
        with self._lock:
            handler = self.message_handlers.get(message.channel_id)
            if handler:
                try:
                    handler(message)
                except Exception as e:
                    print(f"Message handler error: {e}") 