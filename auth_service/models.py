"""
Auth Service Models
Defines Pydantic models for user authentication, authorization, and accounting.
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
    STAFF = "staff"


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    """User response model"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithPermissions(User):
    """User with their permissions"""
    permissions: List[str]


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User


class TokenPayload(BaseModel):
    """JWT token payload"""
    user_id: int
    email: str
    role: UserRole
    exp: datetime


class AuditLog(BaseModel):
    """Audit log entry for accounting"""
    id: int
    user_id: int
    action: str  # e.g., "login", "register", "role_change", "access_denied"
    resource: str  # e.g., "user", "report", "settings"
    status: str  # "success" or "failure"
    ip_address: str
    timestamp: datetime
    details: Optional[dict] = None
    
    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """Base permission model"""
    name: str
    description: Optional[str] = None


class Permission(PermissionBase):
    """Permission response model"""
    id: int
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base role model"""
    name: UserRole
    description: Optional[str] = None


class Role(RoleBase):
    """Role with permissions"""
    id: int
    permissions: List[Permission]
    
    class Config:
        from_attributes = True
