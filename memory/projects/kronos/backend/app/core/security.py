"""
Security & Authentication
JWT tokens, password hashing, encryption
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import base64
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()

# Encryption (for sensitive data at rest)
_fernet_key = None


def get_fernet():
    """Get or create Fernet encryption instance"""
    global _fernet_key
    if _fernet_key is None:
        if settings.ENCRYPTION_KEY:
            _fernet_key = Fernet(settings.ENCRYPTION_KEY.encode())
        else:
            # Generate a key for development (NOT for production!)
            key = Fernet.generate_key()
            _fernet_key = Fernet(key)
            logger.warning("Using auto-generated encryption key (development only)")
    return _fernet_key


# Password Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# JWT Token Functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning("JWT decode error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Encryption Functions (for sensitive data)
def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    fernet = get_fernet()
    encrypted = fernet.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    fernet = get_fernet()
    decoded = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted = fernet.decrypt(decoded)
    return decrypted.decode()


# Dependency for protected routes
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract and validate current user from token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return int(user_id)


# Role-based access control decorator
def require_role(required_role: str):
    """Dependency to check user role"""
    async def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
        token = credentials.credentials
        payload = decode_token(token)
        
        user_role = payload.get("role")
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return int(payload.get("sub"))
    
    return role_checker
