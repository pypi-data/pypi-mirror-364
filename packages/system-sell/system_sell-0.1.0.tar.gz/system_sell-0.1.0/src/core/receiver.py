"""
File Receiver - Handles receiving files from senders
"""

import asyncio
import socket
import struct
import json
import hashlib
from pathlib import Path
from typing import Optional

from ..utils.encryption import FileEncryption
from ..utils.session import SessionManager
from ..utils.network import NetworkUtils
from ..utils.progress import ProgressTracker


class FileReceiver:
    """Handles receiving files via P2P connection"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session_manager = SessionManager()
        self.network_utils = NetworkUtils(config)
        self.encryption = FileEncryption()
        
    async def receive_file(self, session_code: str, output_path: Optional[str] = None) -> None:
        """Receive a file from a sender"""
        
        # Resolve sender's address via session code
        sender_info = await self._resolve_sender(session_code)
        
        if not sender_info:
            raise ConnectionError(f"Could not find sender for session: {session_code}")
        
        # Connect to sender
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            host, port = sender_info['host'], sender_info['port']
            self.logger.info(f"[✓] Connecting to {host}:{port}")
            
            client_socket.connect((host, port))
            self.logger.info(f"[✓] Connected to sender")
            
            # Receive file
            await self._receive_file_data(client_socket, output_path)
            
        finally:
            client_socket.close()
    
    async def _receive_file_data(self, socket: socket.socket, output_path: Optional[str]) -> None:
        """Receive file data from connected sender"""
        
        # Receive encryption key and metadata
        encryption_key, metadata = await self._receive_metadata(socket)
        
        filename = metadata['filename']
        file_size = metadata['size']
        expected_checksum = metadata['checksum']
        
        # Determine output path
        if output_path:
            output_file = Path(output_path)
            if output_file.is_dir():
                output_file = output_file / filename
        else:
            output_file = Path(filename)
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"[✓] Receiving: {filename} ({file_size} bytes)")
        
        # Receive encrypted file data with progress tracking
        progress = ProgressTracker(file_size, filename)
        
        with open(output_file, 'wb') as f:
            bytes_received = 0
            
            while True:
                # Receive chunk size
                chunk_size_data = self._receive_exact(socket, 4)
                if not chunk_size_data:
                    break
                
                chunk_size = struct.unpack('!I', chunk_size_data)[0]
                
                # End marker
                if chunk_size == 0:
                    break
                
                # Receive encrypted chunk
                encrypted_chunk = self._receive_exact(socket, chunk_size)
                if not encrypted_chunk:
                    break
                
                # Decrypt chunk
                decrypted_chunk = self.encryption.decrypt_data(encrypted_chunk, encryption_key)
                
                # Write to file
                f.write(decrypted_chunk)
                bytes_received += len(decrypted_chunk)
                progress.update(len(decrypted_chunk))
        
        # Verify checksum
        actual_checksum = self._calculate_checksum(output_file)
        if actual_checksum != expected_checksum:
            output_file.unlink()  # Delete corrupted file
            raise ValueError("File integrity check failed")
        
        self.logger.info(f"[✓] File received successfully: {output_file}")
    
    async def _receive_metadata(self, socket: socket.socket) -> tuple:
        """Receive metadata and encryption key from sender"""
        
        # Receive key
        key_length_data = self._receive_exact(socket, 4)
        key_length = struct.unpack('!I', key_length_data)[0]
        encryption_key = self._receive_exact(socket, key_length)
        
        # Receive metadata
        metadata_length_data = self._receive_exact(socket, 4)
        metadata_length = struct.unpack('!I', metadata_length_data)[0]
        metadata_json = self._receive_exact(socket, metadata_length)
        
        metadata = json.loads(metadata_json.decode('utf-8'))
        
        return encryption_key, metadata
    
    def _receive_exact(self, socket: socket.socket, length: int) -> bytes:
        """Receive exact number of bytes from socket"""
        data = b''
        while len(data) < length:
            chunk = socket.recv(length - len(data))
            if not chunk:
                break
            data += chunk
        return data
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    async def _resolve_sender(self, session_code: str) -> Optional[dict]:
        """Resolve sender's address from session code (defaults to port 8000 for local testing)"""
        # TODO: Implement session resolution via STUN server
        # For now, return a placeholder
        return {
            'host': '127.0.0.1',  # Localhost for testing
            'port': 8000
        }
