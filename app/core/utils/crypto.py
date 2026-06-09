import base64
import os
import hashlib
import logging
from cryptography.fernet import Fernet
from app.config import settings

logger = logging.getLogger(__name__)

def _get_encryption_key() -> bytes:
    """
    Generates a 32-byte urlsafe base64-encoded key from the POWERBI_CRYPTO_KEY environment variable.
    Falls back to settings.SECRET_KEY if the specific crypto key is not provided.
    """
    key_str = os.getenv("POWERBI_CRYPTO_KEY")
    if not key_str:
        key_str = settings.SECRET_KEY
    
    # Fernet requires exactly a 32-byte urlsafe base64-encoded key.
    # We take the SHA-256 hash of the string to ensure a deterministic 32-byte sequence,
    # then base64url-encode it.
    key_hash = hashlib.sha256(key_str.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(key_hash)

def encrypt_password(plain_password: str) -> str:
    """
    Encrypts a plain password using Fernet symmetric encryption.
    Returns a string containing the encrypted token.
    """
    if not plain_password:
        return ""
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = fernet.encrypt(plain_password.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Error encrypting password: {e}")
        return ""

def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypts a Fernet encrypted password.
    Returns the decrypted plain text password.
    """
    if not encrypted_password:
        return ""
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        decrypted_bytes = fernet.decrypt(encrypted_password.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decrypt password: {e}")
        # In case the password was stored as plain-text before, return empty or handle safely
        return ""
