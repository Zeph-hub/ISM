# ISM Microservices: API Design & Best Practices Guide

This document provides comprehensive best practices for developing and maintaining the ISM (Integrated Services Management) microservices architecture.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [AAA Implementation (Authentication, Authorization, Accounting)](#aaa-implementation)
3. [API Design Best Practices](#api-design-best-practices)
4. [Data Modeling](#data-modeling)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Security Best Practices](#security-best-practices)
8. [Service Communication](#service-communication)
9. [Deployment](#deployment)

---

## Architecture Overview

### Microservices Structure

```
API Gateway (Port 8000) - Main entry point
    ├── Auth Service (Port 8001) - Authentication, Authorization, Accounting
    ├── Curriculum Service (Port 8002) - Course & curriculum management
    ├── Notification Service (Port 8003) - Notification management
    ├── Finance Service (Port 8004) - Financial management
    ├── Student Service (Port 8005) - Student management
    └── Staff Service (Port 8006) - Staff management
```

### Design Patterns

- **API Gateway Pattern**: Gateway service routes and proxies requests to microservices
- **Database per Service**: Each service manages its own data
- **Service Registry**: Services communicate via HTTP/REST with known service URLs
- **Asynchronous Communication**: Notifications use background tasks for bulk operations

---

## AAA Implementation (Authentication, Authorization, Accounting)

### 1. Authentication (AuthN)

**Definition**: Verifying user identity

**Best Practices**:

```python
# ✅ DO: Use JWT tokens with expiration
access_token = f"access_token_{user['id']}_{datetime.utcnow().timestamp()}"
refresh_token = f"refresh_token_{user['id']}_{datetime.utcnow().timestamp()}"

# ✅ DO: Hash passwords using bcrypt (in production)
from bcrypt import hashpw, checkpw
hashed_password = hashpw(password.encode(), bcrypt.gensalt())

# ❌ DON'T: Store plain text passwords
# ❌ DON'T: Send credentials over HTTP (use HTTPS only)
# ❌ DON'T: Hardcode tokens
```

**Implementation**:
- Endpoint: `POST /api/auth/login`
- Validates email and password
- Returns access & refresh tokens
- Logs authentication attempts

### 2. Authorization (AuthZ)

**Definition**: Verifying user permissions

**Best Practices**:

```python
# ✅ DO: Use role-based access control (RBAC)
class UserRole(str, Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
    STAFF = "staff"

# ✅ DO: Define granular permissions
permissions_map = {
    UserRole.ADMIN: ["read:users", "write:users", "delete:users"],
    UserRole.STUDENT: ["read:profile", "write:profile", "read:grades"]
}

# ✅ DO: Validate authorization before returning data
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Verify current user has permission to view this user
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

# ❌ DON'T: Trust client-provided role/permission claims
# ❌ DON'T: Store permissions in JWT without validation
```

**Implementation**:
- Endpoint: `POST /api/auth/users/{user_id}/role` (admin only)
- Assigns roles to users
- Maps roles to permissions
- Validates permissions on protected routes

### 3. Accounting (Audit Logging)

**Definition**: Recording user actions for compliance & security

**Best Practices**:

```python
# ✅ DO: Log all sensitive operations
async def log_audit(
    user_id: int = None,
    action: str = None,
    resource: str = None,
    status: str = "success",
    ip_address: str = "127.0.0.1",
    details: dict = None
):
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

# ✅ DO: Include relevant context
# Log actions: "login", "logout", "register", "role_change", "access_denied"

# ✅ DO: Use immutable log storage (database)
# In production, use dedicated audit tables with append-only writes

# ❌ DON'T: Log sensitive data (passwords, tokens, SSN)
# ❌ DON'T: Make logs modifiable after creation
# ❌ DON'T: Forget to log failed attempts
```

**Implementation**:
- Endpoint: `GET /api/auth/audit-logs` (admin only)
- Logs all user actions
- Immutable audit trail
- Filterable by user, action, date range

---

## API Design Best Practices

### 1. RESTful Principles

```python
# ✅ DO: Use proper HTTP methods
GET /api/students                    # List resources
POST /api/students                   # Create resource
GET /api/students/{id}               # Get single resource
PUT /api/students/{id}               # Update resource
DELETE /api/students/{id}            # Delete resource

# ✅ DO: Use meaningful resource names (nouns, not verbs)
GET /api/students/{id}/enrollments   # Get enrollments
# ❌ DON'T: POST /api/students/getEnrollments

# ✅ DO: Use proper status codes
200 OK              # Successful GET, PUT, DELETE
201 Created         # Successful POST
204 No Content      # Successful DELETE with no response body
400 Bad Request     # Invalid input
401 Unauthorized    # Missing/invalid credentials
403 Forbidden       # Authenticated but not authorized
404 Not Found       # Resource doesn't exist
409 Conflict        # Resource conflict (e.g., duplicate ID)
```

### 2. Pagination

```python
# ✅ DO: Always paginate large datasets
@app.get("/api/students")
async def list_students(skip: int = 0, limit: int = 10) -> List[Student]:
    """
    List students with pagination.
    - skip: Number of records to skip (default 0)
    - limit: Number of records to return (default 10, max 100)
    """
    students = list(STUDENTS_DB.values())[skip:skip + limit]
    return [Student(**s) for s in students]

# Usage: GET /api/students?skip=0&limit=10
```

### 3. Filtering & Sorting

```python
# ✅ DO: Support common filters
@app.get("/api/students")
async def list_students(
    skip: int = 0,
    limit: int = 10,
    status: StudentStatus = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[Student]:
    students = list(STUDENTS_DB.values())
    
    # Filter
    if status:
        students = [s for s in students if s["status"] == status]
    
    # Sort
    reverse = sort_order == "desc"
    students = sorted(students, key=lambda x: x[sort_by], reverse=reverse)
    
    # Paginate
    return [Student(**s) for s in students[skip:skip + limit]]
```

### 4. Versioning

```python
# ✅ DO: Version your APIs
@app.get("/api/v1/students")
@app.get("/api/v2/students")  # For breaking changes

# Alternative: Use headers
# X-API-Version: 1.0

# ❌ DON'T: Make breaking changes without versioning
```

### 5. Request/Response Format

```python
# ✅ DO: Use Pydantic models for validation
from pydantic import BaseModel, EmailStr, Field

class StudentCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    
    class Config:
        example = {
            "email": "john@example.com",
            "full_name": "John Doe",
            "phone": "+1-234-567-8900"
        }

# ✅ DO: Provide consistent error responses
{
    "status": "error",
    "code": "INVALID_INPUT",
    "message": "Validation failed",
    "details": {
        "email": "Invalid email format"
    }
}

# ✅ DO: Document with OpenAPI/Swagger
@app.get("/api/students/{student_id}")
async def get_student(student_id: int) -> Student:
    """
    Get a specific student by ID.
    
    **Path Parameters**:
    - student_id: The unique identifier of the student
    
    **Responses**:
    - 200: Student found
    - 404: Student not found
    """
    ...
```

---

## Data Modeling

### 1. Schema Design

```python
# ✅ DO: Separate create, update, and response models
class StudentBase(BaseModel):
    email: EmailStr
    full_name: str

class StudentCreate(StudentBase):
    """For POST requests"""
    phone: Optional[str] = None

class StudentUpdate(BaseModel):
    """For PUT requests - all fields optional"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class Student(StudentBase):
    """Response model with read-only fields"""
    id: int
    status: StudentStatus
    enrollment_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True  # For ORM models
```

### 2. Relationships

```python
# ✅ DO: Denormalize for read operations
class StudentWithEnrollments(Student):
    """Include related data for complex queries"""
    enrollments: List[Enrollment] = []
    grades: List[Grade] = []

# ❌ DON'T: Always return all related data
# Instead, use separate endpoints for deep relationships

# Usage:
# GET /api/students/{id}              # Returns Student
# GET /api/students/{id}/profile      # Returns StudentWithEnrollments
# GET /api/students/{id}/enrollments  # Returns List[Enrollment]
```

### 3. Soft Deletes

```python
# ✅ DO: Use soft delete for data integrity
@app.delete("/api/students/{student_id}")
async def delete_student(student_id: int):
    """
    Deactivate a student (soft delete).
    Maintains referential integrity and audit trail.
    """
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(status_code=404)
    
    student["status"] = StudentStatus.INACTIVE
    # Record still exists in database
    # Audit log created automatically

# ❌ DON'T: Hard delete without backup
```

---

## Error Handling

### 1. Error Responses

```python
# ✅ DO: Return consistent error format
from fastapi import HTTPException

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={
        "error": "student_not_found",
        "message": "Student with ID 123 not found",
        "timestamp": datetime.utcnow().isoformat()
    }
)

# ✅ DO: Include error codes for client handling
response = {
    "status": "error",
    "code": "INVALID_EMAIL",
    "message": "Email format is invalid",
    "field": "email"
}

# ✅ DO: Log errors with context
import logging
logger = logging.getLogger(__name__)

@app.get("/api/students/{student_id}")
async def get_student(student_id: int):
    try:
        student = STUDENTS_DB.get(student_id)
        if not student:
            logger.warning(f"Student {student_id} not found")
            raise HTTPException(status_code=404)
        return Student(**student)
    except Exception as e:
        logger.error(f"Error retrieving student: {str(e)}", exc_info=True)
        raise
```

### 2. Validation Errors

```python
# ✅ DO: Use Pydantic for automatic validation
class StudentCreate(BaseModel):
    email: EmailStr  # Validates email format
    full_name: str = Field(..., min_length=1, max_length=100)
    student_id: str = Field(..., pattern=r"^[A-Z]{2}\d{6}$")  # Custom pattern

# Pydantic automatically returns 422 Unprocessable Entity with details

# ✅ DO: Validate business logic
@app.post("/api/students")
async def create_student(student_data: StudentCreate):
    # Check uniqueness
    if any(s["student_id"] == student_data.student_id for s in STUDENTS_DB.values()):
        raise HTTPException(
            status_code=400,
            detail=f"Student ID {student_data.student_id} already exists"
        )
```

---

## Performance Optimization

### 1. Caching

```python
# ✅ DO: Cache frequently accessed data
from functools import lru_cache
from datetime import datetime, timedelta

cache = {}
cache_expiry = {}

async def get_course_cached(course_id: int):
    """Cache course data for 5 minutes"""
    if course_id in cache:
        if datetime.utcnow() < cache_expiry.get(course_id, datetime.now()):
            return cache[course_id]
    
    course = COURSES_DB.get(course_id)
    cache[course_id] = course
    cache_expiry[course_id] = datetime.utcnow() + timedelta(minutes=5)
    return course

# Better: Use Redis in production
# from redis import Redis
# redis_client = Redis(host='localhost', port=6379)
```

### 2. Query Optimization

```python
# ✅ DO: Filter data in database (not in Python)
# ✅ DO: Use pagination for large results
@app.get("/api/students")
async def list_students(skip: int = 0, limit: int = 10):
    """Pagination is essential for performance"""
    students = list(STUDENTS_DB.values())[skip:skip + limit]
    return students

# ❌ DON'T: Return all records and filter in code
# ❌ DON'T: Fetch unnecessary related data
```

### 3. Denormalization

```python
# ✅ DO: Denormalize for read-heavy operations
class StudentWithEnrollments(Student):
    """Include enrollment count and recent grades"""
    enrollment_count: int
    average_gpa: float
    recent_grades: List[Grade]

# Instead of:
# 1. Query students
# 2. Query enrollments for each student (N+1 problem)
# 3. Calculate GPA

# Do:
# 1. Query pre-computed view/denormalized data
```

---

## Security Best Practices

### 1. Authentication & Tokens

```python
# ✅ DO: Use HTTPS only
# Configured at reverse proxy or load balancer level

# ✅ DO: Implement token expiration
TOKEN_EXPIRY = timedelta(hours=1)
REFRESH_TOKEN_EXPIRY = timedelta(days=7)

# ✅ DO: Use refresh token rotation
@app.post("/api/auth/refresh")
async def refresh_token(refresh_token: str):
    # Validate refresh token
    # Issue new access token
    # Update refresh token
    pass

# ✅ DO: Implement token blacklist
BLACKLISTED_TOKENS = set()

@app.post("/api/auth/logout")
async def logout(token: str):
    BLACKLISTED_TOKENS.add(token)
    return {"message": "Logged out"}

# ❌ DON'T: Store tokens in local storage (XSS vulnerability)
# ❌ DON'T: Use symmetric keys for JWT (use RS256)
```

### 2. Input Validation

```python
# ✅ DO: Validate all input
from pydantic import validator

class StudentCreate(BaseModel):
    email: EmailStr
    full_name: str
    student_id: str
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v.isalnum():
            raise ValueError('Student ID must be alphanumeric')
        return v

# ✅ DO: Sanitize inputs to prevent injection
import re

def sanitize_input(text: str) -> str:
    # Remove potentially dangerous characters
    return re.sub(r'[<>\"\'`;]', '', text)

# ❌ DON'T: Trust client input
# ❌ DON'T: Skip validation for known users
```

### 3. Rate Limiting

```python
# ✅ DO: Implement rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    """Limit login attempts to 5 per minute"""
    pass

# ✅ DO: Rate limit per user and per IP
@limiter.limit("10/minute;100/hour")
async def api_endpoint(request: Request):
    pass
```

### 4. Data Protection

```python
# ✅ DO: Never log sensitive information
logger.info(f"User registered: {user.email}")  # OK
# ❌ log(f"User password: {password}")  # BAD

# ✅ DO: Encrypt sensitive data at rest
from cryptography.fernet import Fernet
cipher = Fernet(key)
encrypted_ssn = cipher.encrypt(ssn.encode())

# ✅ DO: Use CORS properly
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

## Service Communication

### 1. Inter-Service Communication

```python
# ✅ DO: Use HTTP with proper error handling
import httpx

async def call_student_service(student_id: int):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"http://student-service/api/students/{student_id}",
                headers={"Authorization": f"Bearer {service_token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Student service error: {response.status_code}")
                raise HTTPException(status_code=502)
            
            return response.json()
    except httpx.TimeoutException:
        logger.error("Student service timeout")
        raise HTTPException(status_code=503)
    except Exception as e:
        logger.error(f"Error calling student service: {str(e)}")
        raise HTTPException(status_code=502)

# ✅ DO: Implement circuit breaker pattern
# ✅ DO: Use service mesh (Istio) for production
# ✅ DO: Implement retries with exponential backoff
```

### 2. Asynchronous Communication

```python
# ✅ DO: Use background tasks for non-blocking operations
from fastapi import BackgroundTasks

@app.post("/api/notifications/bulk")
async def send_bulk_notification(
    bulk_data: BulkNotificationCreate,
    background_tasks: BackgroundTasks
):
    """Send notifications asynchronously"""
    background_tasks.add_task(send_notifications_background, bulk_data)
    return {"status": "processing", "message": "Notifications queued"}

async def send_notifications_background(bulk_data: BulkNotificationCreate):
    for recipient_id in bulk_data.recipient_ids:
        # Send notification
        pass

# Better: Use message queue (RabbitMQ, Kafka) for production
```

---

## Deployment

### 1. Environment Configuration

```python
# ✅ DO: Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
API_KEY = os.getenv("API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

# ✅ DO: Use different configs per environment
if ENVIRONMENT == "production":
    SERVICE_URLS = {
        "auth": "http://auth-service.internal:8001",
        "student": "http://student-service.internal:8005",
    }
else:
    SERVICE_URLS = {
        "auth": "http://localhost:8001",
        "student": "http://localhost:8005",
    }
```

### 2. Logging & Monitoring

```python
# ✅ DO: Implement structured logging
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage
logger.info("User registered", extra={"user_id": 123, "email": "user@example.com"})

# ✅ DO: Monitor key metrics
# - Request latency
# - Error rates
# - Service health
# - Database performance
# Use tools: Prometheus, Grafana, ELK stack

# ✅ DO: Set up alerts
# Alert when:
# - Service down
# - Error rate > 5%
# - Response time > 1s
# - Database connection failures
```

### 3. Running Services

```bash
# Development
python -m uvicorn auth_service.main:app --reload --host 0.0.0.0 --port 8001

# Production
gunicorn auth_service.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Docker
docker build -t auth-service .
docker run -p 8001:8001 -e DATABASE_URL=postgresql://... auth-service
```

### 4. Database Migrations

```python
# ✅ DO: Use migrations for schema changes
# Use Alembic:
alembic init migrations
alembic revision --autogenerate -m "Add user table"
alembic upgrade head

# ✅ DO: Test migrations
# ✅ DO: Version your schema
# ✅ DO: Document breaking changes
```

---

## Testing Best Practices

### 1. Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from auth_service.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_duplicate_email():
    # Create first user
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "full_name": "Test", "password": "pass"}
    )
    
    # Try to create duplicate
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "full_name": "Test2", "password": "pass"}
    )
    assert response.status_code == 400
```

### 2. Integration Tests

```python
# Test service-to-service communication
@pytest.mark.asyncio
async def test_student_enrollment():
    # 1. Create student
    student = await create_student(...)
    
    # 2. Create course
    course = await create_course(...)
    
    # 3. Enroll student
    response = await client.post(
        f"/api/students/{student['id']}/enroll",
        json={"course_id": course['id']}
    )
    assert response.status_code == 201
    assert response.json()["student_id"] == student["id"]
```

---

## Checklist

- [ ] Implement JWT authentication with expiration
- [ ] Hash passwords with bcrypt
- [ ] Implement RBAC with roles and permissions
- [ ] Create audit logging for sensitive operations
- [ ] Use Pydantic models for validation
- [ ] Implement pagination for large datasets
- [ ] Add proper error handling
- [ ] Document APIs with OpenAPI/Swagger
- [ ] Set up CORS correctly
- [ ] Implement rate limiting
- [ ] Use HTTPS in production
- [ ] Monitor service health
- [ ] Set up logging and alerting
- [ ] Test all endpoints thoroughly
- [ ] Use environment variables for config
- [ ] Implement circuit breaker pattern
- [ ] Use background tasks for non-blocking operations
- [ ] Version your APIs
- [ ] Document breaking changes
- [ ] Set up database migrations

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [REST API Best Practices](https://restfulapi.net/)
- [OWASP Security Guidelines](https://owasp.org/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Microservices Patterns](https://microservices.io/)
