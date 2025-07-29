"""
Fake Receiver Terminal - Simulates receiver functionality for testing
"""

import asyncio
import socket
import struct
import json
import hashlib
import tempfile
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.encryption import FileEncryption
from src.utils.session import SessionManager
from src.utils.progress import ProgressTracker


class FakeReceiver:
    """Fake receiver for testing purposes"""
    
    def __init__(self):
        self.encryption = FileEncryption()
        self.session_manager = SessionManager()
        
    async def start_fake_receiver(self, session_code, sender_host="127.0.0.1", sender_port=8000, output_dir=None):
        """Start fake receiver that connects to sender"""
        
        print(f"🔑 Using session code: {session_code}")
        print(f"🔗 Connecting to {sender_host}:{sender_port}")
        
        # Validate session code format
        if not self.session_manager.is_valid_session_code(session_code):
            print(f"❌ Invalid session code format: {session_code}")
            return
        
        # Setup output directory
        if not output_dir:
            output_dir = tempfile.mkdtemp(prefix="system_sell_test_")
            print(f"📁 Output directory: {output_dir}")
        
        # Connect to sender
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            print("⏳ Attempting to connect...")
            client_socket.connect((sender_host, sender_port))
            print("✅ Connected to sender!")
            
            # Receive file
            await self.receive_file_data(client_socket, output_dir)
            
        except ConnectionRefusedError:
            print(f"❌ Connection refused. Make sure sender is running on {sender_host}:{sender_port}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            client_socket.close()
    
    async def receive_file_data(self, socket_conn, output_dir):
        """Receive file data from connected sender"""
        
        # Receive encryption key and metadata
        encryption_key, metadata = self.receive_metadata(socket_conn)
        
        filename = metadata['filename']
        file_size = metadata['size']
        expected_checksum = metadata['checksum']
        
        print(f"📤 Receiving: {filename} ({file_size} bytes)")
        print(f"🔐 Encryption key received")
        
        # Determine output path
        output_file = Path(output_dir) / filename
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Receive encrypted file data
        progress = ProgressTracker(file_size, filename)
        
        with open(output_file, 'wb') as f:
            bytes_received = 0
            
            while True:
                # Receive chunk size
                chunk_size_data = self.receive_exact(socket_conn, 4)
                if not chunk_size_data:
                    break
                
                chunk_size = struct.unpack('!I', chunk_size_data)[0]
                
                # End marker
                if chunk_size == 0:
                    print("\n📝 End of file reached")
                    break
                
                # Receive encrypted chunk
                encrypted_chunk = self.receive_exact(socket_conn, chunk_size)
                if not encrypted_chunk:
                    break
                
                # Decrypt chunk
                try:
                    decrypted_chunk = self.encryption.decrypt_data(encrypted_chunk, encryption_key)
                except Exception as e:
                    print(f"\n❌ Decryption error: {e}")
                    return
                
                # Write to file
                f.write(decrypted_chunk)
                bytes_received += len(decrypted_chunk)
                progress.update(len(decrypted_chunk))
        
        # Verify checksum
        print(f"\n🔍 Verifying file integrity...")
        actual_checksum = self.calculate_checksum(output_file)
        
        if actual_checksum == expected_checksum:
            print("✅ File integrity verified!")
            print(f"📁 File saved to: {output_file}")
            
            # Display file content if it's a text file
            try:
                if output_file.suffix.lower() in ['.txt', '.md', '.py', '.json']:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"\n📄 File content:\n{'-' * 40}")
                        print(content)
                        print('-' * 40)
            except:
                pass  # Binary file or encoding issue
                
        else:
            print("❌ File integrity check failed!")
            print(f"Expected: {expected_checksum}")
            print(f"Actual:   {actual_checksum}")
            output_file.unlink()  # Delete corrupted file
    
    def receive_metadata(self, socket_conn):
        """Receive metadata and encryption key from sender"""
        
        # Receive key
        key_length_data = self.receive_exact(socket_conn, 4)
        key_length = struct.unpack('!I', key_length_data)[0]
        encryption_key = self.receive_exact(socket_conn, key_length)
        
        # Receive metadata
        metadata_length_data = self.receive_exact(socket_conn, 4)
        metadata_length = struct.unpack('!I', metadata_length_data)[0]
        metadata_json = self.receive_exact(socket_conn, metadata_length)
        
        metadata = json.loads(metadata_json.decode('utf-8'))
        
        return encryption_key, metadata
    
    def receive_exact(self, socket_conn, length):
        """Receive exact number of bytes from socket"""
        data = b''
        while len(data) < length:
            chunk = socket_conn.recv(length - len(data))
            if not chunk:
                break
            data += chunk
        return data
    
    def calculate_checksum(self, file_path):
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


async def main():
    """Main function for fake receiver"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fake Receiver for SYSTEM-SELL Testing")
    parser.add_argument('session_code', help='Session code from sender')
    parser.add_argument('--host', default='127.0.0.1', help='Sender host')
    parser.add_argument('--port', type=int, default=8000, help='Sender port')
    parser.add_argument('--output', help='Output directory')
    
    args = parser.parse_args()
    
    fake_receiver = FakeReceiver()
    
    try:
        await fake_receiver.start_fake_receiver(
            session_code=args.session_code,
            sender_host=args.host,
            sender_port=args.port,
            output_dir=args.output
        )
    except KeyboardInterrupt:
        print("\n🛑 Receiver interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    print("🔧 SYSTEM-SELL Fake Receiver Terminal")
    print("=" * 40)
    asyncio.run(main())
