#!/usr/bin/env python3
"""
Chat Client Example

This example demonstrates how to create a chat client using the IPC framework.
It connects to the chat_app application and can send/receive messages in different channels.
"""

import time
import threading
import sys
from ipc_framework import FrameworkClient, Message, MessageType


class ChatClient:
    def __init__(self, username: str, host: str = "localhost", port: int = 8888):
        self.username = username
        self.client = FrameworkClient("chat_app", host, port)
        self.current_channel = "general"
        self.running = False
    
    def connect(self):
        """Connect to the chat server"""
        if self.client.connect():
            print(f"Connected as {self.username}")
            
            # Subscribe to all chat channels
            self.subscribe_to_channel("general")
            self.subscribe_to_channel("tech_talk")
            self.subscribe_to_channel("random")
            
            # Set current channel
            self.switch_channel("general")
            return True
        else:
            print("Failed to connect to server")
            return False
    
    def subscribe_to_channel(self, channel_id: str):
        """Subscribe to a chat channel"""
        def message_handler(message: Message):
            payload = message.payload
            msg_type = payload.get('type', 'unknown')
            
            if msg_type == 'chat_message':
                username = payload.get('username', 'Unknown')
                text = payload.get('text', '')
                if username != self.username:  # Don't show our own messages
                    print(f"\n[{channel_id}] {username}: {text}")
                    self.show_prompt()
            
            elif msg_type == 'user_joined':
                username = payload.get('username', 'Unknown')
                if username != self.username:
                    print(f"\n[{channel_id}] *** {username} joined the channel ***")
                    self.show_prompt()
        
        self.client.subscribe(channel_id, message_handler)
        
        # Send join notification
        self.client.notify(channel_id, {
            'type': 'user_join',
            'username': self.username
        })
    
    def switch_channel(self, channel_id: str):
        """Switch to a different channel"""
        self.current_channel = channel_id
        print(f"Switched to #{channel_id}")
        
        # Send join notification to new channel
        self.client.notify(channel_id, {
            'type': 'user_join',
            'username': self.username
        })
    
    def send_message(self, text: str):
        """Send a chat message to current channel"""
        self.client.request(self.current_channel, {
            'username': self.username,
            'text': text,
            'connection_id': self.client.connection_id
        })
    
    def show_prompt(self):
        """Show the chat prompt"""
        if self.running:
            print(f"[{self.current_channel}] {self.username}: ", end="", flush=True)
    
    def start_chat(self):
        """Start the chat interface"""
        self.running = True
        
        print("\n=== Chat Client ===")
        print("Commands:")
        print("  /join <channel>  - Switch to a channel (general, tech_talk, random)")
        print("  /quit            - Exit the chat")
        print("  <message>        - Send a message to current channel")
        print(f"\nYou are in #{self.current_channel}")
        
        try:
            while self.running:
                self.show_prompt()
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    self.send_message(user_input)
                    print(f"[{self.current_channel}] {self.username}: {user_input}")
        
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect()
    
    def handle_command(self, command: str):
        """Handle chat commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == '/quit':
            self.running = False
            
        elif cmd == '/join' and len(parts) > 1:
            channel = parts[1]
            if channel in ['general', 'tech_talk', 'random']:
                self.switch_channel(channel)
            else:
                print("Available channels: general, tech_talk, random")
                
        elif cmd == '/channels':
            print("Available channels: general, tech_talk, random")
            print(f"Current channel: {self.current_channel}")
            
        elif cmd == '/who':
            print(f"You are {self.username} in #{self.current_channel}")
            
        else:
            print("Unknown command. Available commands: /join, /channels, /who, /quit")
    
    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        self.client.disconnect()
        print("\nDisconnected from chat server.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python chat_client.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    client = ChatClient(username)
    
    if client.connect():
        client.start_chat()
    else:
        print("Failed to connect to server. Make sure the server is running.")
        sys.exit(1)


if __name__ == "__main__":
    main() 