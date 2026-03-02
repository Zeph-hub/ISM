"""
Auth Service Routes
Implements Authentication, Authorization, and Accounting endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import json
from typing import List
from sqlalchemy.orm import Session
from bcrypt import checkpw, hashpw, gensalt

from models import (
    UserCreate, LoginRequest, TokenResponse, User, AuditLog,
    UserRole, UserWithPermissions, UserUpdate, UserORM, AuditLogORM
)

# import database session for real persistence
from db import SessionLocal

# OAuth2 scheme used for token extraction in dependency functions
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Mock database placeholders (legacy). We will use real database via SQLAlchemy.
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
    # check if email already exists in database
    db: Session = SessionLocal()
    existing = db.query(UserORM).filter(UserORM.email == user_data.email).first()
    if existing:
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
    # hash password
    hashed = hashpw(user_data.password.encode(), gensalt()).decode()
    user_obj = UserORM(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hashed,
        role=UserRole.STUDENT,
        is_active=True,
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    await log_audit(
        user_id=user_obj.id,
        action="register",
        resource="user",
        status="success"
    )
    return User.from_orm(user_obj)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    
    **Best Practice**: Use HTTPS, rate limiting, and JWT with expiration
    """
    # authenticate against actual database
    db: Session = SessionLocal()
    user_obj = db.query(UserORM).filter(UserORM.email == credentials.email).first()

    if not user_obj or not checkpw(credentials.password.encode(), user_obj.password_hash.encode()):
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

    if not user_obj.is_active:
        await log_audit(
            user_id=user_obj.id,
            action="login",
            resource="user",
            status="failure",
            details={"reason": "account_inactive"}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # generate tokens (mock still)
    access_token = f"access_token_{user_obj.id}_{datetime.utcnow().timestamp()}"
    refresh_token = f"refresh_token_{user_obj.id}_{datetime.utcnow().timestamp()}"

    # Log successful login
    await log_audit(
        user_id=user_obj.id,
        action="login",
        resource="user",
        status="success"
    )

    # convert ORM to Pydantic
    user_data = User.from_orm(user_obj)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
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
    db: Session = SessionLocal()
    user_obj = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    permissions = get_permissions_for_role(user_obj.role)
    user_pyd = User.from_orm(user_obj)
    return UserWithPermissions(**user_pyd.dict(), permissions=permissions)


@router.get("/users", response_model=List[User])
async def list_users() -> List[User]:
    """
    List all users (admin only).
    
    **Best Practice**: Implement role-based access control
    """
    db: Session = SessionLocal()
    users = db.query(UserORM).all()
    return [User.from_orm(u) for u in users]


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate) -> User:
    """
    Update user information.
    
    **Best Practice**: Validate ownership and log all modifications
    """
    db: Session = SessionLocal()
    user_obj = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user_update.email:
        user_obj.email = user_update.email
    if user_update.full_name:
        user_obj.full_name = user_update.full_name
    db.commit()
    await log_audit(
        user_id=user_id,
        action="user_update",
        resource="user",
        status="success",
        details={"fields_updated": user_update.dict(exclude_unset=True)}
    )
    return User.from_orm(user_obj)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """
    Deactivate user account.
    
    **Best Practice**: Use soft delete to maintain audit trail
    """
    db: Session = SessionLocal()
    user_obj = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_obj.is_active = False
    db.commit()
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
    db: Session = SessionLocal()
    user_obj = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    old_role = user_obj.role
    user_obj.role = role
    db.commit()
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
    db: Session = SessionLocal()
    query = db.query(AuditLogORM)
    if user_id is not None:
        query = query.filter(AuditLogORM.user_id == user_id)
    if action is not None:
        query = query.filter(AuditLogORM.action == action)
    orm_logs = query.all()
    return [AuditLog.from_orm(l) for l in orm_logs]


@router.get("/audit-logs/{user_id}", response_model=List[AuditLog])
async def get_user_activity(user_id: int) -> List[AuditLog]:
    """
    Get activity log for a specific user.
    
    **Best Practice**: Help admins track suspicious activities
    """
    db: Session = SessionLocal()
    orm_logs = db.query(AuditLogORM).filter(AuditLogORM.user_id == user_id).all()
    return [AuditLog.from_orm(l) for l in orm_logs]


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
    Persist logs to the database (and keep in-memory for backwards compatibility).
    """
    db: Session = SessionLocal()
    # append to legacy list
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

    # also store in real DB
    orm_entry = AuditLogORM(
        user_id=user_id,
        action=action,
        resource=resource,
        status=status,
        ip_address=ip_address,
        timestamp=datetime.utcnow(),
        details=details
    )
    db.add(orm_entry)
    db.commit()



@router.get("/verify", response_model=User)
async def verify_endpoint(token: str = Depends(oauth2_scheme)) -> User:
    """
    Endpoint for other services to verify the access token and retrieve the user.

    This allows the gateway or any internal API to confirm the identity and
    role of the caller before serving protected resources.
    """
    user = await verify_token(token)

    # log that a verification check occurred (accounting)
    await log_audit(
        user_id=user.id,
        action="verify_token",
        resource="auth",
        status="success"
    )
    return user


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
    Verify mock token and return user object.

    **Best Practice**: implement token validation, blacklisting, and rotation
    with a proper JWT library like python-jose and check expiration.
    """
    # In production: use python-jose to decode a JWT and validate claims
    if not token or not token.startswith("access_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # our mock tokens look like "access_token_{user_id}_{timestamp}"
    parts = token.split("_")
    try:
        # user id is the third element (index 2)
        user_id = int(parts[2])
    except (IndexError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token"
        )

    db: Session = SessionLocal()
    user_obj = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user_obj or not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user"
        )
    return User.from_orm(user_obj)
