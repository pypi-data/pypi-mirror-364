"""
Fake Sender Terminal - Simulates sender functionality for testing
"""

import asyncio
import socket
import struct
import json
import os
import tempfile
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.encryption import FileEncryption
from src.utils.session import SessionManager
from src.utils.progress import ProgressTracker


class FakeSender:
    """Fake sender for testing purposes"""
    
    def __init__(self, port=8000):
        self.port = port
        self.encryption = FileEncryption()
        self.session_manager = SessionManager()
        
    async def start_fake_sender(self, test_file_content="Hello, this is a test file!"):
        """Start fake sender that creates a test file and waits for receiver"""
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_file_content)
            test_file_path = f.name
        
        try:
            print(f"📁 Created test file: {test_file_path}")
            print(f"📄 Content: {test_file_content}")
            
            # Generate session code
            session_code = self.session_manager.generate_session_code()
            print(f"🔑 Session Code: {session_code}")
            
            # Setup server socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                server_socket.bind(('127.0.0.1', self.port))
                server_socket.listen(1)
                
                print(f"🚀 Fake sender listening on port {self.port}")
                print(f"💡 To receive, run: python tests/fake_receiver.py {session_code}")
                print("⏳ Waiting for receiver...")
                
                # Accept connection
                client_socket, addr = server_socket.accept()
                print(f"✅ Connected to receiver at {addr[0]}:{addr[1]}")
                
                # Send file
                await self.send_file_data(client_socket, test_file_path)
                
            finally:
                server_socket.close()
                
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
                print(f"🗑️ Cleaned up test file: {test_file_path}")
    
    async def send_file_data(self, client_socket, file_path):
        """Send file data to connected client"""
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        file_name = file_path.name
        
        print(f"📤 Sending file: {file_name} ({file_size} bytes)")
        
        # Generate encryption key
        encryption_key = self.encryption.generate_key()
        
        # Calculate checksum
        checksum = self.calculate_checksum(file_path)
        
        # Prepare metadata
        metadata = {
            'filename': file_name,
            'size': file_size,
            'checksum': checksum
        }
        
        # Send encryption key and metadata
        self.send_metadata(client_socket, metadata, encryption_key)
        
        # Send encrypted file data
        progress = ProgressTracker(file_size, file_name)
        
        with open(file_path, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < file_size:
                chunk = f.read(1024)  # 1KB chunks for testing
                if not chunk:
                    break
                
                # Encrypt chunk
                encrypted_chunk = self.encryption.encrypt_data(chunk, encryption_key)
                
                # Send chunk size then chunk
                chunk_size = len(encrypted_chunk)
                client_socket.send(struct.pack('!I', chunk_size))
                client_socket.send(encrypted_chunk)
                
                bytes_sent += len(chunk)
                progress.update(len(chunk))
        
        # Send end marker
        client_socket.send(struct.pack('!I', 0))
        print("✅ File sent successfully!")
    
    def send_metadata(self, socket_conn, metadata, key):
        """Send metadata and encryption key to receiver"""
        metadata_json = json.dumps(metadata).encode('utf-8')
        
        # Send key length, key, metadata length, metadata
        socket_conn.send(struct.pack('!I', len(key)))
        socket_conn.send(key)
        socket_conn.send(struct.pack('!I', len(metadata_json)))
        socket_conn.send(metadata_json)
    
    def calculate_checksum(self, file_path):
        """Calculate SHA-256 checksum of file"""
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


async def main():
    """Main function for fake sender"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fake Sender for SYSTEM-SELL Testing")
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    parser.add_argument('--content', default="Hello, this is a test file!", help='Test file content')
    
    args = parser.parse_args()
    
    fake_sender = FakeSender(port=args.port)
    
    try:
        await fake_sender.start_fake_sender(test_file_content=args.content)
    except KeyboardInterrupt:
        print("\n🛑 Sender interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    print("🔧 SYSTEM-SELL Fake Sender Terminal")
    print("=" * 40)
    asyncio.run(main())
