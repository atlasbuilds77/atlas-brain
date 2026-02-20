"""
Python implementation of AES-256-GCM decryption
Compatible with meridian-dashboard's TypeScript encryption (lib/crypto/encryption.ts)
"""
import os
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import logging

log = logging.getLogger("meridian.crypto")

# Must match TypeScript: crypto.scryptSync(key, 'meridian-salt', 32)
SCRYPT_SALT = b'meridian-salt'


def _derive_key() -> bytes:
    """Derive 256-bit key from ENCRYPTION_KEY env var (matches TypeScript scryptSync)"""
    raw_key = os.environ.get("ENCRYPTION_KEY")
    if not raw_key:
        raise ValueError("ENCRYPTION_KEY environment variable is required")
    if len(raw_key) < 32:
        raise ValueError("ENCRYPTION_KEY must be at least 32 characters")
    
    # Node.js crypto.scryptSync(key, salt, 32) defaults:
    # N=16384 (2^14), r=8, p=1
    kdf = Scrypt(
        salt=SCRYPT_SALT,
        length=32,
        n=16384,
        r=8,
        p=1,
        backend=default_backend(),
    )
    return kdf.derive(raw_key.encode('utf-8'))


def decrypt_api_key(encrypted_b64: str, iv_b64: str, auth_tag_b64: str) -> str:
    """
    Decrypt an API key encrypted by the TypeScript encryptApiKey function.
    
    Args:
        encrypted_b64: Base64-encoded ciphertext
        iv_b64: Base64-encoded initialization vector
        auth_tag_b64: Base64-encoded GCM auth tag
    
    Returns:
        Decrypted plaintext string
    """
    key = _derive_key()
    
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(encrypted_b64)
    auth_tag = base64.b64decode(auth_tag_b64)
    
    # AESGCM expects ciphertext + auth_tag concatenated
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext + auth_tag, None)
    
    return plaintext.decode('utf-8')


if __name__ == "__main__":
    # Quick test
    print("Testing key derivation...")
    try:
        key = _derive_key()
        print(f"✅ Key derived: {len(key)} bytes")
    except Exception as e:
        print(f"❌ Key derivation failed: {e}")
        print("   Set ENCRYPTION_KEY env var first")
