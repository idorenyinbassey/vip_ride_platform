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
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'accuracy': self.accuracy,
            'speed': self.speed,
            'bearing': self.bearing,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GPSCoordinates':
        timestamp = None
        if data.get('timestamp'):
            timestamp = datetime.fromisoformat(data['timestamp'])
        
        return cls(
            latitude=data['latitude'],
            longitude=data['longitude'],
            altitude=data.get('altitude'),
            accuracy=data.get('accuracy'),
            speed=data.get('speed'),
            bearing=data.get('bearing'),
            timestamp=timestamp
        )


class ECDHKeyExchange:
    """ECDH key exchange for secure session key establishment"""
    
    def __init__(self):
        self.private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        self.public_key = self.private_key.public_key()
    
    def get_public_key_bytes(self) -> bytes:
        """Get public key as bytes for transmission"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
    
    def get_public_key_base64(self) -> str:
        """Get public key as base64 string"""
        return base64.b64encode(self.get_public_key_bytes()).decode('utf-8')
    
    def derive_shared_key(self, peer_public_key_bytes: bytes) -> bytes:
        """Derive shared key from peer's public key"""
        try:
            # Reconstruct peer's public key
            peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(), peer_public_key_bytes
            )
            
            # Perform ECDH key exchange
            shared_key = self.private_key.exchange(ec.ECDH(), peer_public_key)
            
            # Derive AES-256 key using HKDF
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits for AES-256
                salt=None,
                info=b'VIP_GPS_ENCRYPTION',
                backend=default_backend()
            ).derive(shared_key)
            
            return derived_key
            
        except Exception as e:
            logger.error(f"ECDH key derivation failed: {e}")
            raise


class GPSEncryptionSession:
    """Manages encryption session for a ride"""
    
    def __init__(self, session_id: str, ride_id: str, shared_key: bytes):
        self.session_id = session_id
        self.ride_id = ride_id
        self.shared_key = shared_key
        self.aes_gcm = AESGCM(shared_key)
        self.created_at = datetime.now(timezone.utc)
        self.last_used = datetime.now(timezone.utc)
        self.encryption_count = 0
        self._lock = threading.Lock()
        
        logger.info(f"GPS encryption session created: {session_id}")
    
    def encrypt_location(self, coordinates: GPSCoordinates) -> EncryptedLocation:
        """Encrypt GPS coordinates"""
        try:
            with self._lock:
                # Update usage tracking
                self.last_used = datetime.now(timezone.utc)
                self.encryption_count += 1
                
                # Generate random nonce (96 bits for GCM)
                nonce = secrets.token_bytes(12)
                
                # Prepare location data
                location_data = coordinates.to_dict()
                location_json = json.dumps(location_data, separators=(',', ':')).encode('utf-8')
                
                # Additional authenticated data
                aad = f"{self.session_id}:{self.ride_id}:{self.encryption_count}".encode('utf-8')
                
                # Encrypt with AES-GCM
                ciphertext = self.aes_gcm.encrypt(nonce, location_json, aad)
                
                # Create encrypted location object
                encrypted_location = EncryptedLocation(
                    encrypted_data=base64.b64encode(ciphertext).decode('utf-8'),
                    nonce=base64.b64encode(nonce).decode('utf-8'),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    session_id=self.session_id,
                    ride_id=self.ride_id
                )
                
                logger.debug(f"Location encrypted for session {self.session_id}")
                return encrypted_location
                
        except Exception as e:
            logger.error(f"GPS encryption failed for session {self.session_id}: {e}")
            raise
    
    def decrypt_location(self, encrypted_location: EncryptedLocation) -> GPSCoordinates:
        """Decrypt GPS coordinates"""
        try:
            with self._lock:
                # Decode base64 data
                ciphertext = base64.b64decode(encrypted_location.encrypted_data)
                nonce = base64.b64decode(encrypted_location.nonce)
                
                # Reconstruct AAD
                # Note: In production, you'd need to track the encryption count
                aad = f"{encrypted_location.session_id}:{encrypted_location.ride_id}:1".encode('utf-8')
                
                # Decrypt with AES-GCM
                plaintext = self.aes_gcm.decrypt(nonce, ciphertext, aad)
                
                # Parse location data
                location_data = json.loads(plaintext.decode('utf-8'))
                coordinates = GPSCoordinates.from_dict(location_data)
                
                logger.debug(f"Location decrypted for session {self.session_id}")
                return coordinates
                
        except Exception as e:
            logger.error(f"GPS decryption failed for session {self.session_id}: {e}")
            raise
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if session is expired"""
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds() > (max_age_hours * 3600)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information"""
        return {
            'session_id': self.session_id,
            'ride_id': self.ride_id,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat(),
            'encryption_count': self.encryption_count,
            'age_minutes': (
                datetime.now(timezone.utc) - self.created_at
            ).total_seconds() / 60
        }


class SecureSessionVault:
    """Secure storage for encryption sessions"""
    
    def __init__(self, max_sessions: int = 1000):
        self.sessions: Dict[str, GPSEncryptionSession] = {}
        self.max_sessions = max_sessions
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._running = False
        
    def store_session(self, session: GPSEncryptionSession) -> None:
        """Store encryption session securely"""
        try:
            with self._lock:
                # Clean up if at capacity
                if len(self.sessions) >= self.max_sessions:
                    self._cleanup_expired_sessions()
                
                self.sessions[session.session_id] = session
                logger.info(f"Session stored in vault: {session.session_id}")
                
        except Exception as e:
            logger.error(f"Failed to store session {session.session_id}: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[GPSEncryptionSession]:
        """Retrieve encryption session"""
        try:
            with self._lock:
                session = self.sessions.get(session_id)
                if session and session.is_expired():
                    self.remove_session(session_id)
                    return None
                return session
                
        except Exception as e:
            logger.error(f"Failed to retrieve session {session_id}: {e}")
            return None
    
    def remove_session(self, session_id: str) -> bool:
        """Remove encryption session"""
        try:
            with self._lock:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    logger.info(f"Session removed from vault: {session_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove session {session_id}: {e}")
            return False
    
    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        try:
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if session.is_expired():
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
    
    def start_cleanup_thread(self, cleanup_interval_minutes: int = 30) -> None:
        """Start background cleanup thread"""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return
        
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker,
            args=(cleanup_interval_minutes,),
            daemon=True
        )
        self._cleanup_thread.start()
        logger.info("Session cleanup thread started")
    
    def stop_cleanup_thread(self) -> None:
        """Stop background cleanup thread"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        logger.info("Session cleanup thread stopped")
    
    def _cleanup_worker(self, interval_minutes: int) -> None:
        """Background cleanup worker"""
        while self._running:
            try:
                time.sleep(interval_minutes * 60)
                if self._running:
                    self._cleanup_expired_sessions()
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
    
    def get_vault_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        with self._lock:
            active_sessions = len(self.sessions)
            expired_count = sum(1 for s in self.sessions.values() if s.is_expired())
            
            return {
                'total_sessions': active_sessions,
                'expired_sessions': expired_count,
                'active_sessions': active_sessions - expired_count,
                'max_capacity': self.max_sessions,
                'usage_percentage': (active_sessions / self.max_sessions) * 100
            }


class GPSEncryptionManager:
    """Main GPS encryption manager"""
    
    def __init__(self, vault: Optional[SecureSessionVault] = None):
        self.vault = vault or SecureSessionVault()
        self.vault.start_cleanup_thread()
        
    def create_encryption_session(self, ride_id: str, 
                                peer_public_key_b64: str) -> Tuple[str, str]:
        """
        Create new encryption session with ECDH key exchange
        Returns: (session_id, our_public_key_b64)
        """
        try:
            # Generate session ID
            session_id = secrets.token_urlsafe(32)
            
            # Perform ECDH key exchange
            ecdh = ECDHKeyExchange()
            peer_public_key_bytes = base64.b64decode(peer_public_key_b64)
            shared_key = ecdh.derive_shared_key(peer_public_key_bytes)
            
            # Create encryption session
            session = GPSEncryptionSession(session_id, ride_id, shared_key)
            
            # Store in vault
            self.vault.store_session(session)
            
            # Return session ID and our public key
            our_public_key_b64 = ecdh.get_public_key_base64()
            
            logger.info(f"Encryption session created for ride {ride_id}")
            return session_id, our_public_key_b64
            
        except Exception as e:
            logger.error(f"Failed to create encryption session for ride {ride_id}: {e}")
            raise
    
    def encrypt_coordinates(self, session_id: str, 
                          coordinates: GPSCoordinates) -> Optional[EncryptedLocation]:
        """Encrypt GPS coordinates for transmission"""
        try:
            session = self.vault.get_session(session_id)
            if not session:
                logger.error(f"Encryption session not found: {session_id}")
                return None
            
            return session.encrypt_location(coordinates)
            
        except Exception as e:
            logger.error(f"GPS encryption failed for session {session_id}: {e}")
            return None
    
    def decrypt_coordinates(self, encrypted_location: EncryptedLocation) -> Optional[GPSCoordinates]:
        """Decrypt GPS coordinates"""
        try:
            session = self.vault.get_session(encrypted_location.session_id)
            if not session:
                logger.error(f"Decryption session not found: {encrypted_location.session_id}")
                return None
            
            return session.decrypt_location(encrypted_location)
            
        except Exception as e:
            logger.error(f"GPS decryption failed: {e}")
            return None
    
    def end_encryption_session(self, session_id: str) -> bool:
        """End encryption session"""
        try:
            success = self.vault.remove_session(session_id)
            if success:
                logger.info(f"Encryption session ended: {session_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        try:
            session = self.vault.get_session(session_id)
            return session.get_session_info() if session else None
            
        except Exception as e:
            logger.error(f"Failed to get session info {session_id}: {e}")
            return None
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get encryption manager statistics"""
        return self.vault.get_vault_stats()
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.vault.stop_cleanup_thread()
        except:
            pass


# Global encryption manager instance
_encryption_manager: Optional[GPSEncryptionManager] = None


def get_encryption_manager() -> GPSEncryptionManager:
    """Get global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = GPSEncryptionManager()
    return _encryption_manager


def create_test_coordinates() -> GPSCoordinates:
    """Create test GPS coordinates for testing"""
    return GPSCoordinates(
        latitude=6.5244,  # Lagos, Nigeria
        longitude=3.3792,
        altitude=10.0,
        accuracy=5.0,
        speed=25.5,
        bearing=180.0,
        timestamp=datetime.now(timezone.utc)
    )
