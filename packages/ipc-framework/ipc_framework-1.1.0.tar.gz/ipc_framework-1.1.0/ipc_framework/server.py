"""
Socket-based server implementation for the IPC Framework
"""

import socket
import threading
import json
import select
from typing import Dict, Set, Optional
from .core import IPCServer, Message, MessageType
from .exceptions import ConnectionError, RoutingError, SerializationError


class FrameworkServer(IPCServer):
    """Socket-based IPC Server implementation"""
    
    def __init__(self, host: str = "localhost", port: int = 8888, max_connections: int = 100):
        super().__init__(host, port)
        self.max_connections = max_connections
        self.server_socket: Optional[socket.socket] = None
        self.client_sockets: Dict[str, socket.socket] = {}
        self.socket_to_connection_id: Dict[socket.socket, str] = {}
        self.running = False
        self.server_thread: Optional[threading.Thread] = None
        self._clients_lock = threading.RLock()
    
    def start(self):
        """Start the IPC server"""
        if self.running:
            return
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            self.running = True
            
            print(f"IPC Server started on {self.host}:{self.port}")
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
        except Exception as e:
            raise ConnectionError(f"Failed to start server: {e}")
    
    def stop(self):
        """Stop the IPC server"""
        if not self.running:
            return
        
        self.running = False
        
        # Close all client connections
        with self._clients_lock:
            for client_socket in list(self.client_sockets.values()):
                try:
                    client_socket.close()
                except:
                    pass
            self.client_sockets.clear()
            self.socket_to_connection_id.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Wait for server thread to finish
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1.0)
        
        print("IPC Server stopped")
    
    def _run_server(self):
        """Main server loop"""
        while self.running:
            try:
                # Use select to avoid blocking when server is stopping
                ready_sockets, _, _ = select.select([self.server_socket], [], [], 1.0)
                
                if ready_sockets and self.running:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New client connected from {client_address}")
                    
                    # Start client handler thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, client_address):
        """Handle individual client connection"""
        connection_id = None
        
        try:
            # Wait for initial connection message with app_id
            data = self._receive_message(client_socket)
            if not data:
                return
            
            # Parse connection message
            try:
                message = Message.from_json(data)
                if message.message_type != MessageType.REQUEST or not message.payload.get('action') == 'connect':
                    print(f"Invalid connection message from {client_address}")
                    return
                
                connection_id = message.payload.get('connection_id')
                app_id = message.app_id
                
                if not connection_id or not app_id:
                    print(f"Missing connection_id or app_id from {client_address}")
                    return
                
            except Exception as e:
                print(f"Failed to parse connection message: {e}")
                return
            
            # Register the connection
            with self._clients_lock:
                self.client_sockets[connection_id] = client_socket
                self.socket_to_connection_id[client_socket] = connection_id
                self.connection_manager.add_connection(connection_id, client_socket, app_id)
            
            # Create or get application
            app = self.create_application(app_id)
            print(f"Client {connection_id} connected to application {app_id}")
            
            # Send connection acknowledgment
            ack_message = Message(
                message_id="",
                app_id=app_id,
                channel_id="system",
                message_type=MessageType.RESPONSE,
                payload={'status': 'connected', 'connection_id': connection_id},
                timestamp=0
            )
            self.send_to_connection(client_socket, ack_message)
            
            # Handle messages from this client
            while self.running:
                try:
                    data = self._receive_message(client_socket)
                    if not data:
                        break
                    
                    message = Message.from_json(data)
                    
                    # Auto-create channel if it doesn't exist
                    if not app.get_channel(message.channel_id):
                        app.create_channel(message.channel_id)
                    
                    # Route the message
                    if not self.route_message(message):
                        print(f"Failed to route message: {message.to_dict()}")
                        
                except Exception as e:
                    print(f"Error handling message from {connection_id}: {e}")
                    break
                    
        except Exception as e:
            print(f"Client handler error for {client_address}: {e}")
        
        finally:
            # Clean up connection
            if connection_id:
                with self._clients_lock:
                    self.client_sockets.pop(connection_id, None)
                    self.socket_to_connection_id.pop(client_socket, None)
                    self.connection_manager.remove_connection(connection_id)
                print(f"Client {connection_id} disconnected")
            
            try:
                client_socket.close()
            except:
                pass
    
    def _receive_message(self, client_socket: socket.socket) -> Optional[str]:
        """Receive a message from a client socket"""
        try:
            # First, receive the message length (4 bytes)
            length_data = b""
            while len(length_data) < 4:
                chunk = client_socket.recv(4 - len(length_data))
                if not chunk:
                    return None
                length_data += chunk
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            # Then receive the message data
            message_data = b""
            while len(message_data) < message_length:
                chunk = client_socket.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            
            return message_data.decode('utf-8')
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def send_to_connection(self, connection, message: Message):
        """Send message to a specific connection"""
        try:
            if isinstance(connection, socket.socket):
                self._send_message(connection, message)
            else:
                print(f"Invalid connection type: {type(connection)}")
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def _send_message(self, client_socket: socket.socket, message: Message):
        """Send a message to a client socket"""
        try:
            message_data = message.to_json().encode('utf-8')
            message_length = len(message_data)
            
            # Send message length first (4 bytes)
            length_bytes = message_length.to_bytes(4, byteorder='big')
            client_socket.sendall(length_bytes)
            
            # Send message data
            client_socket.sendall(message_data)
            
        except Exception as e:
            print(f"Error sending message: {e}")
            # Remove broken connection
            connection_id = self.socket_to_connection_id.get(client_socket)
            if connection_id:
                with self._clients_lock:
                    self.client_sockets.pop(connection_id, None)
                    self.socket_to_connection_id.pop(client_socket, None)
                    self.connection_manager.remove_connection(connection_id)
    
    def broadcast_to_application(self, app_id: str, message: Message):
        """Broadcast a message to all connections in an application"""
        connection_ids = self.connection_manager.get_connections_for_app(app_id)
        for connection_id in connection_ids:
            with self._clients_lock:
                client_socket = self.client_sockets.get(connection_id)
                if client_socket:
                    self.send_to_connection(client_socket, message)
    
    def list_applications(self) -> Dict[str, Dict]:
        """Get information about all applications"""
        with self._lock:
            result = {}
            for app_id, app in self.applications.items():
                result[app_id] = {
                    'name': app.name,
                    'channels': app.list_channels(),
                    'connections': len(self.connection_manager.get_connections_for_app(app_id)),
                    'created_at': app.created_at,
                    'last_activity': app.last_activity
                }
            return result
    
    def list_channels(self, app_id: str) -> Dict[str, Dict]:
        """Get information about channels in an application"""
        app = self.get_application(app_id)
        if not app:
            return {}
        
        result = {}
        for channel_id in app.list_channels():
            channel = app.get_channel(channel_id)
            if channel:
                result[channel_id] = {
                    'subscribers': len(channel.get_subscribers()),
                    'created_at': channel.created_at
                }
        return result
    
    def get_stats(self) -> Dict:
        """Get server statistics"""
        with self._lock:
            return {
                'running': self.running,
                'host': self.host,
                'port': self.port,
                'total_applications': len(self.applications),
                'total_connections': len(self.connection_manager.list_connections()),
                'max_connections': self.max_connections
            } 