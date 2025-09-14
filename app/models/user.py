"""
User and authentication data models
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
from datetime import datetime
import re


class UserRole(str, Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"
    DEVELOPER = "developer"
    ENTERPRISE = "enterprise"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class UserCreateRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    company: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserInfo(BaseModel):
    """User information"""
    id: str
    email: EmailStr
    full_name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.PENDING_VERIFICATION)
    tier: UserTier = Field(default=UserTier.FREE)
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    email_verified: bool = Field(default=False)
    two_factor_enabled: bool = Field(default=False)
    api_keys_count: int = Field(default=0)
    total_spent: float = Field(default=0.0)
    credit_balance: float = Field(default=0.0)
    monthly_quota: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)


class UserUpdateRequest(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    two_factor_enabled: Optional[bool] = None


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str
    remember_me: bool = Field(default=False)


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer")
    expires_in: int
    user: UserInfo


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class APIKey(BaseModel):
    """API Key model"""
    id: str
    name: str
    key_preview: str = Field(..., description="First 8 characters of the key")
    created_at: datetime
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)
    rate_limit: Optional[int] = None
    is_active: bool = Field(default=True)


class APIKeyCreateRequest(BaseModel):
    """API Key creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
    permissions: List[str] = Field(default_factory=lambda: ["read", "write"])
    rate_limit: Optional[int] = Field(None, ge=1)


class APIKeyResponse(BaseModel):
    """API Key creation response"""
    key: str = Field(..., description="Full API key - only shown once")
    key_info: APIKey


class UserUsageStats(BaseModel):
    """User usage statistics"""
    user_id: str
    period: str = Field(..., description="Period: daily, weekly, monthly")
    gpu_hours: float
    instances_created: int
    total_cost: float
    credits_used: float
    api_calls: int
    data_transferred_gb: float
    average_instance_duration_hours: float
    most_used_gpu: Optional[str] = None
    most_used_region: Optional[str] = None


class BillingInfo(BaseModel):
    """User billing information"""
    user_id: str
    payment_method: Optional[str] = None
    billing_address: Optional[Dict[str, str]] = None
    tax_id: Optional[str] = None
    currency: str = Field(default="USD")
    auto_recharge: bool = Field(default=False)
    auto_recharge_amount: float = Field(default=100.0)
    auto_recharge_threshold: float = Field(default=10.0)
    invoices: List[Dict[str, Any]] = Field(default_factory=list)
