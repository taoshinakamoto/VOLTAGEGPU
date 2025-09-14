"""
Authentication endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.models.user import (
    UserCreateRequest,
    UserInfo,
    LoginRequest,
    LoginResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    APIKeyCreateRequest,
    APIKeyResponse,
    TokenRefreshRequest
)
from app.models.response import APIResponse
from app.services.auth import AuthService
from app.api.deps import get_current_user

router = APIRouter()
auth_service = AuthService()


@router.post("/register", response_model=APIResponse[UserInfo])
async def register(request: UserCreateRequest):
    """Register a new user account"""
    try:
        # Hash password
        hashed_password = auth_service.get_password_hash(request.password)
        
        # Mock user creation - in production, this would save to database
        user = UserInfo(
            id="user_" + request.email.replace("@", "_").replace(".", "_"),
            email=request.email,
            full_name=request.full_name,
            company=request.company,
            phone=request.phone,
            country=request.country,
            role="user",
            status="pending_verification",
            tier="free",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            email_verified=False,
            credit_balance=10.0  # Free credits on signup
        )
        
        # Generate verification token
        verification_token = auth_service.generate_verification_token(request.email)
        logger.info(f"User registered: {request.email}, verification token: {verification_token[:20]}...")
        
        return APIResponse(
            success=True,
            data=user,
            message="Registration successful. Please check your email to verify your account."
        )
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(request: LoginRequest):
    """Login with email and password"""
    try:
        # Mock authentication - in production, this would check database
        if request.email == "demo@voltagegpu.com" and request.password == "Demo123!":
            # Create tokens
            access_token = auth_service.create_access_token({"sub": "demo_user_id"})
            refresh_token = auth_service.create_refresh_token("demo_user_id")
            
            # Mock user
            user = UserInfo(
                id="demo_user_id",
                email=request.email,
                full_name="Demo User",
                role="user",
                status="active",
                tier="professional",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                email_verified=True,
                credit_balance=1000.0
            )
            
            response = LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
                expires_in=auth_service.access_token_expire * 60,
                user=user
            )
            
            return APIResponse(
                success=True,
                data=response,
                message="Login successful"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=APIResponse[LoginResponse])
async def refresh_token(request: TokenRefreshRequest):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = auth_service.verify_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = payload.get("sub")
        
        # Create new tokens
        access_token = auth_service.create_access_token({"sub": user_id})
        new_refresh_token = auth_service.create_refresh_token(user_id)
        
        # Mock user
        user = UserInfo(
            id=user_id,
            email="user@example.com",
            full_name="User",
            role="user",
            status="active",
            tier="professional",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            email_verified=True,
            credit_balance=1000.0
        )
        
        response = LoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            expires_in=auth_service.access_token_expire * 60,
            user=user
        )
        
        return APIResponse(
            success=True,
            data=response,
            message="Token refreshed successfully"
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout", response_model=APIResponse[dict])
async def logout(current_user: UserInfo = Depends(get_current_user)):
    """Logout current user"""
    try:
        # In production, this would invalidate the token in cache/database
        logger.info(f"User {current_user.id} logged out")
        
        return APIResponse(
            success=True,
            data={"message": "Logged out successfully"},
            message="Logout successful"
        )
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/password-reset", response_model=APIResponse[dict])
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset email"""
    try:
        # Generate reset token
        reset_token = auth_service.generate_password_reset_token(request.email)
        logger.info(f"Password reset requested for {request.email}, token: {reset_token[:20]}...")
        
        # In production, this would send an email
        return APIResponse(
            success=True,
            data={"message": "If the email exists, a reset link has been sent"},
            message="Password reset email sent"
        )
    except Exception as e:
        logger.error(f"Password reset request failed: {str(e)}")
        # Don't reveal if email exists
        return APIResponse(
            success=True,
            data={"message": "If the email exists, a reset link has been sent"},
            message="Password reset email sent"
        )


@router.post("/password-reset/confirm", response_model=APIResponse[dict])
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset with token"""
    try:
        # Verify reset token
        email = auth_service.verify_password_reset_token(request.token)
        
        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Hash new password
        hashed_password = auth_service.get_password_hash(request.new_password)
        
        # In production, this would update the password in database
        logger.info(f"Password reset confirmed for {email}")
        
        return APIResponse(
            success=True,
            data={"message": "Password reset successful"},
            message="Password has been reset successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")


@router.post("/api-keys", response_model=APIResponse[APIKeyResponse])
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Create a new API key"""
    try:
        # Generate API key
        api_key = auth_service.generate_api_key(current_user.id, request.name)
        
        # Mock API key info
        key_info = {
            "id": f"key_{current_user.id}_{request.name.replace(' ', '_')}",
            "name": request.name,
            "key_preview": api_key[:8],
            "created_at": "2024-01-01T00:00:00Z",
            "permissions": request.permissions,
            "rate_limit": request.rate_limit,
            "is_active": True
        }
        
        response = APIKeyResponse(
            key=api_key,
            key_info=key_info
        )
        
        return APIResponse(
            success=True,
            data=response,
            message="API key created successfully. Save this key securely as it won't be shown again."
        )
    except Exception as e:
        logger.error(f"API key creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify-email/{token}", response_model=APIResponse[dict])
async def verify_email(token: str):
    """Verify email address with token"""
    try:
        email = auth_service.verify_email_token(token)
        
        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # In production, this would update user's email_verified status
        logger.info(f"Email verified for {email}")
        
        return APIResponse(
            success=True,
            data={"email": email},
            message="Email verified successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
