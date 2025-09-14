"""
API dependencies
"""

from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from loguru import logger

from app.services.auth import AuthService
from app.models.user import UserInfo

security = HTTPBearer()
auth_service = AuthService()


async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validate API key from Authorization header
    
    Args:
        credentials: Bearer token from header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    api_key = credentials.credentials
    
    # Check if it's an API key (starts with vgpu_)
    if api_key.startswith("vgpu_"):
        user_id = auth_service.verify_api_key(api_key)
        if user_id:
            logger.info(f"API key authenticated for user: {user_id}")
            return api_key
        else:
            logger.warning(f"Invalid API key: {api_key[:10]}...")
            raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Otherwise, treat it as a JWT token
    try:
        payload = auth_service.verify_token(api_key)
        logger.info(f"JWT token authenticated for user: {payload.get('sub')}")
        return api_key
    except Exception as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


async def get_current_user(
    api_key: str = Depends(get_api_key)
) -> UserInfo:
    """
    Get current user from API key or token
    
    Args:
        api_key: Valid API key or JWT token
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    # Mock user for now - in production, this would query the database
    return UserInfo(
        id="mock_user_id",
        email="user@example.com",
        full_name="Mock User",
        role="user",
        status="active",
        tier="professional",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        email_verified=True,
        credit_balance=1000.0
    )


async def get_optional_api_key(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Get optional API key from header
    
    Args:
        authorization: Authorization header
        
    Returns:
        API key if provided and valid, None otherwise
    """
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        return None
    
    api_key = authorization.replace("Bearer ", "")
    
    if api_key.startswith("vgpu_"):
        user_id = auth_service.verify_api_key(api_key)
        if user_id:
            return api_key
    
    return None


async def require_admin(
    current_user: UserInfo = Depends(get_current_user)
) -> UserInfo:
    """
    Require admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
