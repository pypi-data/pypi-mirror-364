"""
File Sender - Handles sending files to receivers
"""

import asyncio
import socket
import struct
import hashlib
import os
from pathlib import Path
from typing import Optional

from ..utils.encryption import FileEncryption
from ..utils.session import SessionManager
from ..utils.network import NetworkUtils
from ..utils.progress import ProgressTracker


class FileSender:
    """Handles sending files via P2P connection"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session_manager = SessionManager()
        self.network_utils = NetworkUtils(config)
        self.encryption = FileEncryption()
        
    async def send_file(self, file_path: str, show_qr: bool = False, port: int = 8000) -> None:
        """Send a file to a receiver"""
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate session code
        session_code = self.session_manager.generate_session_code()
        
        # Setup server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            # Bind to port 8000 by default
            server_socket.bind(('0.0.0.0', port))
            actual_port = server_socket.getsockname()[1]
            server_socket.listen(1)
            
            self.logger.info(f"[✓] Waiting for receiver...")
            self.logger.info(f"[✓] Share this code: {session_code}")
            
            if show_qr:
                self._show_qr_code(session_code)
            
            # Register session with STUN server for NAT traversal
            await self._register_session(session_code, actual_port)
            
            # Wait for connection
            client_socket, addr = server_socket.accept()
            self.logger.info(f"[✓] Connected to {addr[0]}:{addr[1]}")
            
            # Send file
            await self._send_file_data(client_socket, file_path_obj)
            
        finally:
            server_socket.close()
    
    async def _send_file_data(self, client_socket: socket.socket, file_path: Path) -> None:
        """Send file data to connected client"""
        file_size = file_path.stat().st_size
        file_name = file_path.name
        
        # Generate encryption key for this session
        encryption_key = self.encryption.generate_key()
        
        # Send file metadata
        metadata = {
            'filename': file_name,
            'size': file_size,
            'checksum': self._calculate_checksum(file_path)
        }
        
        # Send encryption key and metadata
        await self._send_metadata(client_socket, metadata, encryption_key)
        
        # Send encrypted file data with progress tracking
        progress = ProgressTracker(file_size, file_name)
        
        with open(file_path, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < file_size:
                chunk = f.read(8192)  # 8KB chunks
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
        
        self.logger.info(f"[✓] File sent successfully: {file_name}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    async def _send_metadata(self, socket: socket.socket, metadata: dict, key: bytes) -> None:
        """Send metadata and encryption key to receiver"""
        import json
        
        # Create metadata packet
        metadata_json = json.dumps(metadata).encode('utf-8')
        
        # Send key length, key, metadata length, metadata
        socket.send(struct.pack('!I', len(key)))
        socket.send(key)
        socket.send(struct.pack('!I', len(metadata_json)))
        socket.send(metadata_json)
    
    async def _register_session(self, session_code: str, port: int) -> None:
        """Register session with STUN server for NAT traversal"""
        # TODO: Implement STUN server registration
        pass
    
    def _show_qr_code(self, session_code: str) -> None:
        """Display QR code for session code"""
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=2, border=1)
            qr.add_data(session_code)
            qr.make(fit=True)
            qr.print_ascii(invert=True)
        except ImportError:
            self.logger.warning("QR code display requires 'qrcode' package")
            self.logger.info("Install with: pip install qrcode[pil]")
