"""
Auth Service Routes
Implements Authentication, Authorization, and Accounting endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
import json
from typing import List
from .models import (
    UserCreate, LoginRequest, TokenResponse, User, AuditLog,
    UserRole, UserWithPermissions, UserUpdate
)

# Mock database - In production, use actual database
USERS_DB = {}
AUDIT_LOGS_DB = []
MOCK_USER_ID_COUNTER = 1

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ===== AUTHENTICATION =====
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> User:
    """
    Register a new user.
    
    **Best Practice**: Always validate email uniqueness and password strength
    """
    global MOCK_USER_ID_COUNTER
    
    # Check if user already exists
    if any(u["email"] == user_data.email for u in USERS_DB.values()):
        # Log failed registration attempt
        await log_audit(
            action="register",
            resource="user",
            status="failure",
            details={"reason": "email_already_exists"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # In production: hash password using bcrypt
    user_id = MOCK_USER_ID_COUNTER
    MOCK_USER_ID_COUNTER += 1
    
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password": user_data.password,  # In production: use bcrypt.hashpw()
        "role": UserRole.STUDENT,  # Default role
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    USERS_DB[user_id] = new_user
    
    # Log successful registration
    await log_audit(
        user_id=user_id,
        action="register",
        resource="user",
        status="success"
    )
    
    return User(**new_user)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    
    **Best Practice**: Use HTTPS, rate limiting, and JWT with expiration
    """
    # Find user by email
    user = next((u for u in USERS_DB.values() if u["email"] == credentials.email), None)
    
    if not user or user["password"] != credentials.password:
        # Log failed login attempt
        await log_audit(
            action="login",
            resource="user",
            status="failure",
            details={"email": credentials.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user["is_active"]:
        await log_audit(
            user_id=user["id"],
            action="login",
            resource="user",
            status="failure",
            details={"reason": "account_inactive"}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Generate tokens (mock - use python-jose in production)
    access_token = f"access_token_{user['id']}_{datetime.utcnow().timestamp()}"
    refresh_token = f"refresh_token_{user['id']}_{datetime.utcnow().timestamp()}"
    
    # Log successful login
    await log_audit(
        user_id=user["id"],
        action="login",
        resource="user",
        status="success"
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=User(**user)
    )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    
    **Best Practice**: Validate token expiration and rotation
    """
    # In production: validate refresh token JWT
    # For now, just create new access token
    new_access_token = f"access_token_{datetime.utcnow().timestamp()}"
    return {"access_token": new_access_token, "token_type": "bearer"}


# ===== AUTHORIZATION =====
@router.get("/users/{user_id}", response_model=UserWithPermissions)
async def get_user(user_id: int) -> UserWithPermissions:
    """
    Get user with their permissions.
    
    **Best Practice**: Always verify authorization before returning sensitive data
    """
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Mock permissions based on role
    permissions = get_permissions_for_role(user["role"])
    
    return UserWithPermissions(**user, permissions=permissions)


@router.get("/users", response_model=List[User])
async def list_users() -> List[User]:
    """
    List all users (admin only).
    
    **Best Practice**: Implement role-based access control
    """
    return [User(**u) for u in USERS_DB.values()]


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate) -> User:
    """
    Update user information.
    
    **Best Practice**: Validate ownership and log all modifications
    """
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.email:
        user["email"] = user_update.email
    if user_update.full_name:
        user["full_name"] = user_update.full_name
    
    # Log change
    await log_audit(
        user_id=user_id,
        action="user_update",
        resource="user",
        status="success",
        details={"fields_updated": user_update.dict(exclude_unset=True)}
    )
    
    return User(**user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """
    Deactivate user account.
    
    **Best Practice**: Use soft delete to maintain audit trail
    """
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["is_active"] = False
    
    await log_audit(
        user_id=user_id,
        action="user_deactivate",
        resource="user",
        status="success"
    )


@router.post("/users/{user_id}/role")
async def assign_role(user_id: int, role: UserRole):
    """
    Assign role to user (admin only).
    
    **Best Practice**: Implement approval workflow for sensitive operations
    """
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_role = user["role"]
    user["role"] = role
    
    # Log role change
    await log_audit(
        user_id=user_id,
        action="role_change",
        resource="user",
        status="success",
        details={"old_role": old_role, "new_role": role}
    )
    
    return {"message": f"User role changed from {old_role} to {role}"}


# ===== ACCOUNTING (Audit Logging) =====
@router.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(user_id: int = None, action: str = None) -> List[AuditLog]:
    """
    Retrieve audit logs (admin only).
    
    **Best Practice**: Filter logs by date range and immutable storage
    """
    logs = AUDIT_LOGS_DB
    
    if user_id:
        logs = [log for log in logs if log.get("user_id") == user_id]
    
    if action:
        logs = [log for log in logs if log.get("action") == action]
    
    return logs


@router.get("/audit-logs/{user_id}", response_model=List[AuditLog])
async def get_user_activity(user_id: int) -> List[AuditLog]:
    """
    Get activity log for a specific user.
    
    **Best Practice**: Help admins track suspicious activities
    """
    return [log for log in AUDIT_LOGS_DB if log.get("user_id") == user_id]


@router.post("/audit-logs")
async def create_audit_log(action: str, resource: str, status: str, details: dict = None):
    """
    Manually create an audit log entry.
    
    **Best Practice**: Centralize audit logging for consistency
    """
    log_entry = {
        "id": len(AUDIT_LOGS_DB) + 1,
        "user_id": None,
        "action": action,
        "resource": resource,
        "status": status,
        "ip_address": "127.0.0.1",
        "timestamp": datetime.utcnow(),
        "details": details
    }
    AUDIT_LOGS_DB.append(log_entry)
    return log_entry


# ===== HELPER FUNCTIONS =====
async def log_audit(
    user_id: int = None,
    action: str = None,
    resource: str = None,
    status: str = "success",
    ip_address: str = "127.0.0.1",
    details: dict = None
):
    """
    Log user action for audit trail.
    This is the accounting component of AAA.
    """
    log_entry = {
        "id": len(AUDIT_LOGS_DB) + 1,
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "status": status,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow(),
        "details": details
    }
    AUDIT_LOGS_DB.append(log_entry)


def get_permissions_for_role(role: UserRole) -> List[str]:
    """
    Get permissions assigned to a role.
    This is the authorization component of AAA.
    """
    permissions_map = {
        UserRole.ADMIN: [
            "read:users",
            "write:users",
            "delete:users",
            "read:audit_logs",
            "read:finances",
            "write:finances"
        ],
        UserRole.INSTRUCTOR: [
            "read:students",
            "write:students",
            "read:curriculum",
            "write:curriculum",
            "read:grades"
        ],
        UserRole.STUDENT: [
            "read:profile",
            "write:profile",
            "read:grades",
            "read:curriculum"
        ],
        UserRole.STAFF: [
            "read:all",
            "write:finance",
            "write:staff"
        ]
    }
    return permissions_map.get(role, [])


async def verify_token(token: str) -> User:
    """
    Verify JWT token and return user.
    
    **Best Practice**: Implement token validation, blacklisting, and rotation
    """
    # In production: use python-jose to decode JWT
    # For now, mock validation
    if not token.startswith("access_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return None
