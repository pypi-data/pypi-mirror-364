"""
Socket-based client implementation for the IPC Framework
"""

import socket
import threading
import time
import json
from typing import Optional, Callable, Dict, Any
from .core import IPCClient, Message, MessageType
from .exceptions import ConnectionError, SerializationError


class FrameworkClient(IPCClient):
    """Socket-based IPC Client implementation"""
    
    def __init__(self, app_id: str, host: str = "localhost", port: int = 8888, connection_timeout: float = 10.0):
        super().__init__(app_id, host, port)
        self.connection_timeout = connection_timeout
        self.socket: Optional[socket.socket] = None
        self.receive_thread: Optional[threading.Thread] = None
        self.pending_responses: Dict[str, Any] = {}  # message_id -> response data
        self.response_handlers: Dict[str, Callable] = {}  # message_id -> handler
        self._socket_lock = threading.RLock()
        self._response_lock = threading.RLock()
    
    def connect(self) -> bool:
        """Connect to the IPC server"""
        if self.connected:
            return True
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.connection_timeout)
            self.socket.connect((self.host, self.port))
            
            # Send connection message
            connect_message = Message(
                message_id="",
                app_id=self.app_id,
                channel_id="system",
                message_type=MessageType.REQUEST,
                payload={
                    'action': 'connect',
                    'connection_id': self.connection_id
                },
                timestamp=0
            )
            
            self._send_message(connect_message)
            
            # Wait for acknowledgment
            ack_data = self._receive_message()
            if ack_data:
                ack_message = Message.from_json(ack_data)
                if (ack_message.message_type == MessageType.RESPONSE and 
                    ack_message.payload.get('status') == 'connected'):
                    self.connected = True
                    
                    # Start receive thread
                    self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
                    self.receive_thread.start()
                    
                    print(f"Connected to IPC server as {self.app_id}:{self.connection_id}")
                    return True
            
            print("Failed to receive connection acknowledgment")
            return False
            
        except Exception as e:
            print(f"Connection failed: {e}")
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            return False
    
    def disconnect(self):
        """Disconnect from the IPC server"""
        if not self.connected:
            return
        
        self.connected = False
        
        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Wait for receive thread to finish
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
        
        print(f"Disconnected from IPC server")
    
    def _send_message(self, message: Message) -> str:
        """Internal method to send message"""
        if not self.connected and message.message_type != MessageType.REQUEST:
            raise ConnectionError("Not connected to server")
        
        try:
            with self._socket_lock:
                if not self.socket:
                    raise ConnectionError("Socket is not available")
                
                message_data = message.to_json().encode('utf-8')
                message_length = len(message_data)
                
                # Send message length first (4 bytes)
                length_bytes = message_length.to_bytes(4, byteorder='big')
                self.socket.sendall(length_bytes)
                
                # Send message data
                self.socket.sendall(message_data)
                
                return message.message_id
                
        except Exception as e:
            raise ConnectionError(f"Failed to send message: {e}")
    
    def _receive_message(self) -> Optional[str]:
        """Receive a message from the server"""
        try:
            with self._socket_lock:
                if not self.socket:
                    return None
                
                # First, receive the message length (4 bytes)
                length_data = b""
                while len(length_data) < 4:
                    chunk = self.socket.recv(4 - len(length_data))
                    if not chunk:
                        return None
                    length_data += chunk
                
                message_length = int.from_bytes(length_data, byteorder='big')
                
                # Then receive the message data
                message_data = b""
                while len(message_data) < message_length:
                    chunk = self.socket.recv(message_length - len(message_data))
                    if not chunk:
                        return None
                    message_data += chunk
                
                return message_data.decode('utf-8')
                
        except Exception as e:
            if self.connected:
                print(f"Error receiving message: {e}")
            return None
    
    def _receive_loop(self):
        """Background thread for receiving messages"""
        while self.connected:
            try:
                data = self._receive_message()
                if not data:
                    break
                
                message = Message.from_json(data)
                
                # Check if this is a response to a pending request
                if message.reply_to:
                    with self._response_lock:
                        if message.reply_to in self.response_handlers:
                            handler = self.response_handlers.pop(message.reply_to)
                            try:
                                handler(message)
                            except Exception as e:
                                print(f"Response handler error: {e}")
                        else:
                            # Store response for sync requests
                            self.pending_responses[message.reply_to] = message
                else:
                    # Handle regular messages
                    self.handle_message(message)
                    
            except Exception as e:
                if self.connected:
                    print(f"Receive loop error: {e}")
                break
        
        # Connection lost
        if self.connected:
            print("Connection to server lost")
            self.connected = False
    
    def send_request(self, channel_id: str, data: Any, timeout: float = 5.0) -> Optional[Message]:
        """Send a request and wait for response"""
        message_id = self.request(channel_id, data)
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self._response_lock:
                if message_id in self.pending_responses:
                    return self.pending_responses.pop(message_id)
            time.sleep(0.01)
        
        return None  # Timeout
    
    def send_request_async(self, channel_id: str, data: Any, callback: Callable[[Message], None]) -> str:
        """Send a request with async callback"""
        message_id = self.request(channel_id, data)
        
        with self._response_lock:
            self.response_handlers[message_id] = callback
        
        return message_id
    
    def notify(self, channel_id: str, data: Any) -> str:
        """Send a notification (no response expected)"""
        return self.send_message(channel_id, MessageType.NOTIFICATION, data)
    
    def create_channel_handler(self, channel_id: str, handler: Callable[[Message], None]):
        """Create a handler for a specific channel"""
        with self._lock:
            self.message_handlers[channel_id] = handler
    
    def remove_channel_handler(self, channel_id: str):
        """Remove handler for a channel"""
        with self._lock:
            self.message_handlers.pop(channel_id, None)
    
    def wait_for_message(self, channel_id: str, timeout: float = 5.0) -> Optional[Message]:
        """Wait for a message on a specific channel"""
        received_message = None
        event = threading.Event()
        
        def temp_handler(message: Message):
            nonlocal received_message
            received_message = message
            event.set()
        
        # Set temporary handler
        original_handler = self.message_handlers.get(channel_id)
        self.create_channel_handler(channel_id, temp_handler)
        
        try:
            # Wait for message
            if event.wait(timeout):
                return received_message
            return None
        finally:
            # Restore original handler
            if original_handler:
                self.create_channel_handler(channel_id, original_handler)
            else:
                self.remove_channel_handler(channel_id)
    
    def ping(self, timeout: float = 2.0) -> bool:
        """Ping the server to check connection"""
        try:
            response = self.send_request("system", {"action": "ping"}, timeout)
            return response is not None and response.payload.get("status") == "pong"
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about this connection"""
        return {
            'app_id': self.app_id,
            'connection_id': self.connection_id,
            'connected': self.connected,
            'host': self.host,
            'port': self.port,
            'subscribed_channels': list(self.message_handlers.keys())
        } 