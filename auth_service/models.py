"""
Auth Service Models
Defines Pydantic and SQLAlchemy models for user authentication, authorization, and accounting.
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Base


class UserRole(str, Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
    STAFF = "staff"


# SQLAlchemy ORM Models
class UserORM(Base):
    """User ORM model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    audit_logs = relationship("AuditLogORM", back_populates="user")


class AuditLogORM(Base):
    """Audit log ORM model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # success or failure
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
    
    user = relationship("UserORM", back_populates="audit_logs")


# Pydantic Models (for API validation)
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
    user_id: Optional[int] = None
    action: str  # e.g., "login", "register", "role_change", "access_denied"
    resource: str  # e.g., "user", "report", "settings"
    status: str  # "success" or "failure"
    ip_address: Optional[str] = None
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
