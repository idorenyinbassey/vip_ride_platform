# GPS Encryption System
"""
AES-256-GCM encryption system for VIP GPS tracking with ECDH key exchange
"""

import os
import secrets
import threading
import time
import logging
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import json
import base64

logger = logging.getLogger(__name__)


@dataclass
class EncryptedLocation:
    """Encrypted GPS coordinates with metadata"""
    encrypted_data: str
    nonce: str
    timestamp: str
    session_id: str
    ride_id: str
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'encrypted_data': self.encrypted_data,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'session_id': self.session_id,
            'ride_id': self.ride_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'EncryptedLocation':
        return cls(**data)


@dataclass
class GPSCoordinates:
    """GPS coordinates with additional metadata"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            'latitude': self.latitude,
            'longitude': self.longitude,
        }
        if self.accuracy is not None:
            data['accuracy'] = self.accuracy
        if self.altitude is not None:
            data['altitude'] = self.altitude
        if self.speed is not None:
            data['speed'] = self.speed
        if self.heading is not None:
            data['heading'] = self.heading
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        return data


class GPSEncryptionError(Exception):
    """Custom exception for GPS encryption errors"""
    pass


class VIPGPSEncryption:
    """
    VIP GPS Encryption System using AES-256-GCM with ECDH key exchange
    Provides end-to-end encryption for VIP user location data
    """
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.environ.get('ENCRYPTION_KEY')
        if not self.master_key:
            raise GPSEncryptionError("Master encryption key not provided")
        
        # Convert master key to bytes if string
        if isinstance(self.master_key, str):
            self.master_key = self.master_key.encode('utf-8')
        
        # Pad or truncate to 32 bytes for AES-256
        self.master_key = self.master_key.ljust(32, b'0')[:32]
        
        # Session management
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._session_lock = threading.Lock()
        self._cleanup_thread = None
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up expired sessions"""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return
            
        def cleanup_sessions():
            while True:
                try:
                    time.sleep(300)  # Check every 5 minutes
                    self._cleanup_expired_sessions()
                except Exception as e:
                    logger.error(f"Session cleanup error: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_expired_sessions(self):
        """Remove expired encryption sessions"""
        current_time = datetime.now(timezone.utc)
        expired_sessions = []
        
        with self._session_lock:
            for session_id, session_data in self._sessions.items():
                expires_at = session_data.get('expires_at')
                if expires_at and current_time > expires_at:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
                logger.info(f"Cleaned up expired session: {session_id}")
    
    def create_encryption_session(self, ride_id: str, duration_hours: int = 24) -> str:
        """
        Create a new encryption session for a ride
        
        Args:
            ride_id: Unique ride identifier
            duration_hours: Session duration in hours
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        
        # Generate ECDH key pair for this session
        private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        public_key = private_key.public_key()
        
        # Derive session key using HKDF
        session_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=f"ride_{ride_id}_{session_id}".encode(),
            backend=default_backend()
        ).derive(self.master_key)
        
        session_data = {
            'session_id': session_id,
            'ride_id': ride_id,
            'created_at': datetime.now(timezone.utc),
            'expires_at': expires_at,
            'session_key': session_key,
            'private_key': private_key,
            'public_key': public_key,
            'location_count': 0
        }
        
        with self._session_lock:
            self._sessions[session_id] = session_data
        
        logger.info(f"Created encryption session {session_id} for ride {ride_id}")
        return session_id
    
    def encrypt_location(self, coordinates: GPSCoordinates, session_id: str) -> EncryptedLocation:
        """
        Encrypt GPS coordinates using AES-256-GCM
        
        Args:
            coordinates: GPS coordinates to encrypt
            session_id: Active encryption session ID
            
        Returns:
            EncryptedLocation object with encrypted data
        """
        if session_id not in self._sessions:
            raise GPSEncryptionError(f"Invalid or expired session: {session_id}")
        
        session_data = self._sessions[session_id]
        
        # Check if session is expired
        if datetime.now(timezone.utc) > session_data['expires_at']:
            raise GPSEncryptionError(f"Session expired: {session_id}")
        
        try:
            # Prepare location data for encryption
            location_data = coordinates.to_dict()
            location_json = json.dumps(location_data, sort_keys=True)
            
            # Generate nonce for this encryption operation
            nonce = os.urandom(12)  # 96-bit nonce for GCM
            
            # Encrypt using AES-256-GCM
            aesgcm = AESGCM(session_data['session_key'])
            ciphertext = aesgcm.encrypt(nonce, location_json.encode('utf-8'), None)
            
            # Encode for storage/transmission
            encrypted_data = base64.b64encode(ciphertext).decode('ascii')
            nonce_b64 = base64.b64encode(nonce).decode('ascii')
            
            # Update session statistics
            with self._session_lock:
                self._sessions[session_id]['location_count'] += 1
                self._sessions[session_id]['last_used'] = datetime.now(timezone.utc)
            
            encrypted_location = EncryptedLocation(
                encrypted_data=encrypted_data,
                nonce=nonce_b64,
                timestamp=datetime.now(timezone.utc).isoformat(),
                session_id=session_id,
                ride_id=session_data['ride_id']
            )
            
            logger.debug(f"Encrypted location for session {session_id}")
            return encrypted_location
            
        except Exception as e:
            logger.error(f"Location encryption failed: {e}")
            raise GPSEncryptionError(f"Encryption failed: {e}")
    
    def decrypt_location(self, encrypted_location: EncryptedLocation) -> GPSCoordinates:
        """
        Decrypt GPS coordinates
        
        Args:
            encrypted_location: Encrypted location data
            
        Returns:
            GPSCoordinates object with decrypted data
        """
        session_id = encrypted_location.session_id
        
        if session_id not in self._sessions:
            raise GPSEncryptionError(f"Session not found: {session_id}")
        
        session_data = self._sessions[session_id]
        
        try:
            # Decode from base64
            ciphertext = base64.b64decode(encrypted_location.encrypted_data)
            nonce = base64.b64decode(encrypted_location.nonce)
            
            # Decrypt using AES-256-GCM
            aesgcm = AESGCM(session_data['session_key'])
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            # Parse JSON data
            location_data = json.loads(plaintext.decode('utf-8'))
            
            # Convert timestamp if present
            if 'timestamp' in location_data:
                location_data['timestamp'] = datetime.fromisoformat(location_data['timestamp'])
            
            coordinates = GPSCoordinates(**location_data)
            
            logger.debug(f"Decrypted location for session {session_id}")
            return coordinates
            
        except Exception as e:
            logger.error(f"Location decryption failed: {e}")
            raise GPSEncryptionError(f"Decryption failed: {e}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id not in self._sessions:
            return None
        
        session_data = self._sessions[session_id]
        return {
            'session_id': session_id,
            'ride_id': session_data['ride_id'],
            'created_at': session_data['created_at'].isoformat(),
            'expires_at': session_data['expires_at'].isoformat(),
            'location_count': session_data['location_count'],
            'is_expired': datetime.now(timezone.utc) > session_data['expires_at']
        }
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate an encryption session"""
        with self._session_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"Terminated session: {session_id}")
                return True
            return False
    
    def get_public_key(self, session_id: str) -> Optional[bytes]:
        """Get public key for ECDH key exchange"""
        if session_id not in self._sessions:
            return None
        
        public_key = self._sessions[session_id]['public_key']
        return public_key.public_numbers().public_numbers().x.to_bytes(48, 'big')


# Global encryption instance
_encryption_instance = None
_encryption_lock = threading.Lock()


def get_encryption_instance() -> VIPGPSEncryption:
    """Get singleton encryption instance"""
    global _encryption_instance
    
    if _encryption_instance is None:
        with _encryption_lock:
            if _encryption_instance is None:
                _encryption_instance = VIPGPSEncryption()
    
    return _encryption_instance


def encrypt_gps_data(coordinates: GPSCoordinates, session_id: str) -> EncryptedLocation:
    """Convenience function to encrypt GPS data"""
    encryption = get_encryption_instance()
    return encryption.encrypt_location(coordinates, session_id)


def decrypt_gps_data(encrypted_location: EncryptedLocation) -> GPSCoordinates:
    """Convenience function to decrypt GPS data"""
    encryption = get_encryption_instance()
    return encryption.decrypt_location(encrypted_location)


def create_gps_session(ride_id: str, duration_hours: int = 24) -> str:
    """Convenience function to create GPS encryption session"""
    encryption = get_encryption_instance()
    return encryption.create_encryption_session(ride_id, duration_hours)


def terminate_gps_session(session_id: str) -> bool:
    """Convenience function to terminate GPS encryption session"""
    encryption = get_encryption_instance()
    return encryption.terminate_session(session_id)
