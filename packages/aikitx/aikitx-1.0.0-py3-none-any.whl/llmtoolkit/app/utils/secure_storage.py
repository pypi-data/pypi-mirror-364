"""
Secure Storage Utility

Provides OS-specific secure storage for sensitive data like OAuth tokens.
Falls back to encrypted file storage when OS-specific secure storage is not available.
"""

import logging
import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecureStorageError(Exception):
    """Exception raised for secure storage operations."""
    pass


class SecureStorage:
    """Secure storage manager with OS-specific implementations."""
    
    def __init__(self, app_name: str = "gguf_loader"):
        """
        Initialize secure storage.
        
        Args:
            app_name: Application name for storage identification
        """
        self.logger = logging.getLogger("gguf_loader.secure_storage")
        self.app_name = app_name
        self.os_name = platform.system().lower()
        
        # Try to import OS-specific secure storage libraries
        self.keyring_available = False
        try:
            import keyring
            self.keyring = keyring
            self.keyring_available = True
            self.logger.info("OS keyring available for secure storage")
        except ImportError:
            self.logger.warning("OS keyring not available, using encrypted file storage")
        
        # Set up encrypted file storage as fallback
        self.storage_dir = Path.home() / f".{app_name}" / "secure"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate or load encryption key
        self.key_file = self.storage_dir / "storage.key"
        self._setup_encryption()
    
    def _setup_encryption(self) -> None:
        """Set up encryption for file-based storage."""
        try:
            if self.key_file.exists():
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    key_data = f.read()
                self.cipher = Fernet(key_data)
                self.logger.debug("Loaded existing encryption key")
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions (Unix-like systems)
                if hasattr(os, 'chmod'):
                    os.chmod(self.key_file, 0o600)
                self.cipher = Fernet(key)
                self.logger.info("Generated new encryption key for secure storage")
        except Exception as e:
            self.logger.error(f"Failed to setup encryption: {e}")
            raise SecureStorageError(f"Failed to setup encryption: {e}")
    
    def store_token(self, service: str, username: str, token_data: Dict[str, Any]) -> bool:
        """
        Store OAuth token data securely.
        
        Args:
            service: Service name (e.g., "gmail_oauth")
            username: Username/email for the service
            token_data: Token data dictionary
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            key = f"{self.app_name}_{service}_{username}_tokens"
            token_json = json.dumps(token_data)
            
            if self.keyring_available:
                # Use OS keyring
                self.keyring.set_password(self.app_name, key, token_json)
                self.logger.info(f"Stored tokens for {service}:{username} in OS keyring")
            else:
                # Use encrypted file storage
                encrypted_data = self.cipher.encrypt(token_json.encode())
                token_file = self.storage_dir / f"{service}_{username}_tokens.enc"
                with open(token_file, 'wb') as f:
                    f.write(encrypted_data)
                # Set restrictive permissions
                if hasattr(os, 'chmod'):
                    os.chmod(token_file, 0o600)
                self.logger.info(f"Stored tokens for {service}:{username} in encrypted file")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store tokens for {service}:{username}: {e}")
            return False
    
    def retrieve_token(self, service: str, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve OAuth token data.
        
        Args:
            service: Service name (e.g., "gmail_oauth")
            username: Username/email for the service
            
        Returns:
            Token data dictionary or None if not found
        """
        try:
            key = f"{self.app_name}_{service}_{username}_tokens"
            
            if self.keyring_available:
                # Use OS keyring
                token_json = self.keyring.get_password(self.app_name, key)
                if token_json:
                    self.logger.debug(f"Retrieved tokens for {service}:{username} from OS keyring")
                    return json.loads(token_json)
            else:
                # Use encrypted file storage
                token_file = self.storage_dir / f"{service}_{username}_tokens.enc"
                if token_file.exists():
                    with open(token_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    token_json = decrypted_data.decode()
                    self.logger.debug(f"Retrieved tokens for {service}:{username} from encrypted file")
                    return json.loads(token_json)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve tokens for {service}:{username}: {e}")
            return None
    
    def delete_token(self, service: str, username: str) -> bool:
        """
        Delete OAuth token data.
        
        Args:
            service: Service name (e.g., "gmail_oauth")
            username: Username/email for the service
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            key = f"{self.app_name}_{service}_{username}_tokens"
            
            if self.keyring_available:
                # Use OS keyring
                try:
                    self.keyring.delete_password(self.app_name, key)
                    self.logger.info(f"Deleted tokens for {service}:{username} from OS keyring")
                except self.keyring.errors.PasswordDeleteError:
                    self.logger.debug(f"No tokens found for {service}:{username} in OS keyring")
            else:
                # Use encrypted file storage
                token_file = self.storage_dir / f"{service}_{username}_tokens.enc"
                if token_file.exists():
                    token_file.unlink()
                    self.logger.info(f"Deleted tokens for {service}:{username} from encrypted file")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete tokens for {service}:{username}: {e}")
            return False
    
    def store_credentials_path(self, service: str, username: str, credentials_path: str) -> bool:
        """
        Store credentials file path securely.
        
        Args:
            service: Service name (e.g., "gmail_oauth")
            username: Username/email for the service
            credentials_path: Path to credentials.json file
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            key = f"{self.app_name}_{service}_{username}_credentials_path"
            
            if self.keyring_available:
                # Use OS keyring
                self.keyring.set_password(self.app_name, key, credentials_path)
                self.logger.info(f"Stored credentials path for {service}:{username} in OS keyring")
            else:
                # Use encrypted file storage
                encrypted_data = self.cipher.encrypt(credentials_path.encode())
                cred_file = self.storage_dir / f"{service}_{username}_credentials_path.enc"
                with open(cred_file, 'wb') as f:
                    f.write(encrypted_data)
                # Set restrictive permissions
                if hasattr(os, 'chmod'):
                    os.chmod(cred_file, 0o600)
                self.logger.info(f"Stored credentials path for {service}:{username} in encrypted file")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store credentials path for {service}:{username}: {e}")
            return False
    
    def retrieve_credentials_path(self, service: str, username: str) -> Optional[str]:
        """
        Retrieve credentials file path.
        
        Args:
            service: Service name (e.g., "gmail_oauth")
            username: Username/email for the service
            
        Returns:
            Credentials file path or None if not found
        """
        try:
            key = f"{self.app_name}_{service}_{username}_credentials_path"
            
            if self.keyring_available:
                # Use OS keyring
                credentials_path = self.keyring.get_password(self.app_name, key)
                if credentials_path:
                    self.logger.debug(f"Retrieved credentials path for {service}:{username} from OS keyring")
                    return credentials_path
            else:
                # Use encrypted file storage
                cred_file = self.storage_dir / f"{service}_{username}_credentials_path.enc"
                if cred_file.exists():
                    with open(cred_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    credentials_path = decrypted_data.decode()
                    self.logger.debug(f"Retrieved credentials path for {service}:{username} from encrypted file")
                    return credentials_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve credentials path for {service}:{username}: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if secure storage is available.
        
        Returns:
            True if secure storage is available, False otherwise
        """
        return self.keyring_available or (self.storage_dir.exists() and self.key_file.exists())
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the storage backend.
        
        Returns:
            Dictionary with storage information
        """
        return {
            "keyring_available": self.keyring_available,
            "storage_dir": str(self.storage_dir),
            "os_name": self.os_name,
            "encryption_available": hasattr(self, 'cipher')
        }