#!/usr/bin/env python3
"""
File Sharing Client Example

This example demonstrates how to use the IPC framework for file sharing operations.
It shows request/response patterns and status monitoring.
"""

import time
import random
import threading
from .. import FrameworkClient, Message, MessageType


class FileClient:
    def __init__(self, client_name: str, host: str = "localhost", port: int = 8888):
        self.client_name = client_name
        self.client = FrameworkClient("file_share", host, port)
        self.uploaded_files = []
    
    def connect(self):
        """Connect to the file sharing server"""
        if self.client.connect():
            print(f"File client '{self.client_name}' connected")
            
            # Subscribe to status updates
            self.client.subscribe("status", self.handle_status_update)
            return True
        else:
            print("Failed to connect to server")
            return False
    
    def handle_status_update(self, message: Message):
        """Handle file operation status updates"""
        payload = message.payload
        msg_type = payload.get('type', 'unknown')
        
        if msg_type == 'upload_progress':
            filename = payload.get('filename', 'unknown')
            progress = payload.get('progress', 0)
            status = payload.get('status', 'unknown')
            print(f"[STATUS] Upload {filename}: {progress}% - {status}")
    
    def upload_file(self, filename: str, size: int):
        """Upload a file (simulated)"""
        print(f"Uploading file: {filename} ({size} bytes)")
        
        self.client.request("upload", {
            'filename': filename,
            'size': size,
            'client': self.client_name,
            'connection_id': self.client.connection_id
        })
        
        self.uploaded_files.append(filename)
        print(f"Upload request sent for {filename}")
    
    def download_file(self, filename: str) -> bool:
        """Download a file and wait for response"""
        print(f"Requesting download: {filename}")
        
        response = self.client.send_request("download", {
            'filename': filename,
            'client': self.client_name,
            'connection_id': self.client.connection_id
        }, timeout=5.0)
        
        if response:
            payload = response.payload
            download_url = payload.get('download_url', 'N/A')
            expires_at = payload.get('expires_at', 0)
            expires_in = int(expires_at - time.time())
            
            print(f"Download ready:")
            print(f"  File: {filename}")
            print(f"  URL: {download_url}")
            print(f"  Expires in: {expires_in} seconds")
            return True
        else:
            print(f"Download request timed out for {filename}")
            return False
    
    def list_files(self):
        """List uploaded files"""
        if self.uploaded_files:
            print("Uploaded files:")
            for i, filename in enumerate(self.uploaded_files, 1):
                print(f"  {i}. {filename}")
        else:
            print("No files uploaded yet")
    
    def disconnect(self):
        """Disconnect from the server"""
        self.client.disconnect()
        print(f"File client '{self.client_name}' disconnected")


def simulate_file_operations():
    """Simulate various file operations"""
    # Create multiple clients
    clients = []
    for i in range(3):
        client = FileClient(f"Client_{i+1}")
        if client.connect():
            clients.append(client)
        time.sleep(0.5)
    
    if not clients:
        print("No clients could connect")
        return
    
    print(f"\n=== Starting file operations with {len(clients)} clients ===\n")
    
    # Simulate file uploads
    sample_files = [
        ("document.pdf", 1024000),
        ("image.jpg", 2048000),
        ("video.mp4", 50000000),
        ("data.csv", 512000),
        ("code.zip", 1536000)
    ]
    
    # Each client uploads some files
    for client in clients:
        num_files = random.randint(1, 3)
        selected_files = random.sample(sample_files, num_files)
        
        for filename, size in selected_files:
            client.upload_file(f"{client.client_name}_{filename}", size)
            time.sleep(1)
    
    time.sleep(2)
    print("\n=== Upload phase completed ===\n")
    
    # Simulate downloads
    for client in clients:
        print(f"\n--- {client.client_name} downloads ---")
        client.list_files()
        
        # Try to download some files
        for other_client in clients:
            if other_client != client and other_client.uploaded_files:
                file_to_download = random.choice(other_client.uploaded_files)
                success = client.download_file(file_to_download)
                time.sleep(1)
    
    print("\n=== File operations completed ===")
    
    # Disconnect all clients
    for client in clients:
        client.disconnect()


def interactive_mode():
    """Run in interactive mode"""
    client_name = input("Enter client name: ").strip() or "InteractiveClient"
    client = FileClient(client_name)
    
    if not client.connect():
        return
    
    print("\n=== File Sharing Client ===")
    print("Commands:")
    print("  upload <filename> <size>  - Upload a file")
    print("  download <filename>       - Download a file")
    print("  list                      - List uploaded files")
    print("  quit                      - Exit")
    
    try:
        while True:
            command = input(f"\n[{client_name}] > ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'upload' and len(command) >= 3:
                filename = command[1]
                try:
                    size = int(command[2])
                    client.upload_file(filename, size)
                except ValueError:
                    print("Invalid size. Please enter a number.")
            elif cmd == 'download' and len(command) >= 2:
                filename = command[1]
                client.download_file(filename)
            elif cmd == 'list':
                client.list_files()
            else:
                print("Invalid command or missing arguments")
    
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'sim':
        simulate_file_operations()
    else:
        interactive_mode()


if __name__ == "__main__":
    main() 