"""
Authentication service
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger
import secrets
import string
from app.core.config import settings


class AuthService:
    """Service for handling authentication and authorization"""
    
    def __init__(self):
        """Initialize the auth service"""
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a password
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Data to encode in the token
            expires_delta: Token expiration time
            
        Returns:
            JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token
        
        Args:
            user_id: User ID
            
        Returns:
            Refresh token
        """
        data = {
            "sub": user_id,
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)
        }
        expires_delta = timedelta(days=30)
        return self.create_access_token(data, expires_delta)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Decoded token data
            
        Raises:
            JWTError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise
    
    def generate_api_key(self, user_id: str, key_name: str) -> str:
        """
        Generate a new API key
        
        Args:
            user_id: User ID
            key_name: Name for the API key
            
        Returns:
            API key
        """
        # Generate a secure random API key
        prefix = "vgpu"
        random_part = ''.join(
            secrets.choice(string.ascii_letters + string.digits)
            for _ in range(48)
        )
        api_key = f"{prefix}_{random_part}"
        
        logger.info(f"Generated API key '{key_name}' for user {user_id}")
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """
        Verify an API key and return the associated user ID
        
        Args:
            api_key: API key to verify
            
        Returns:
            User ID if valid, None otherwise
        """
        # In a real implementation, this would check against a database
        # For now, we'll validate the format
        if api_key and api_key.startswith("vgpu_") and len(api_key) == 53:
            # This would normally query the database
            # Return a mock user ID for now
            return "mock_user_id"
        return None
    
    def generate_verification_token(self, email: str) -> str:
        """
        Generate an email verification token
        
        Args:
            email: User email
            
        Returns:
            Verification token
        """
        data = {
            "email": email,
            "type": "email_verification",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)
    
    def verify_email_token(self, token: str) -> Optional[str]:
        """
        Verify an email verification token
        
        Args:
            token: Verification token
            
        Returns:
            Email if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") == "email_verification":
                return payload.get("email")
        except JWTError:
            pass
        return None
    
    def generate_password_reset_token(self, email: str) -> str:
        """
        Generate a password reset token
        
        Args:
            email: User email
            
        Returns:
            Reset token
        """
        data = {
            "email": email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """
        Verify a password reset token
        
        Args:
            token: Reset token
            
        Returns:
            Email if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") == "password_reset":
                return payload.get("email")
        except JWTError:
            pass
        return None
    
    def check_permissions(self, user_role: str, required_permission: str) -> bool:
        """
        Check if a user role has a specific permission
        
        Args:
            user_role: User's role
            required_permission: Required permission
            
        Returns:
            True if user has permission
        """
        permissions = {
            "admin": ["read", "write", "delete", "admin"],
            "developer": ["read", "write", "delete"],
            "user": ["read", "write"],
            "guest": ["read"]
        }
        
        return required_permission in permissions.get(user_role, [])
