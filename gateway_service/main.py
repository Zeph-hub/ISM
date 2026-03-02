from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
import httpx
import uvicorn

app = FastAPI(
    title="API Gateway Service",
    description="Main entry point for ISM microservices",
    version="1.0.0",
    docs_url="/api/docs"
)

# directory for dashboards and other simple HTML
templates = Jinja2Templates(directory="/workspaces/ISM/gateway_service/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs (configure based on deployment)
SERVICE_URLS = {
    "auth": "http://localhost:8001",
    "curriculum": "http://localhost:8002",
    "notification": "http://localhost:8003",
    "finance": "http://localhost:8004",
    "student": "http://localhost:8005",
    "staff": "http://localhost:8006"
}


@app.get("/")
async def root():
    """API Gateway - Main entry point"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "description": "Main entry point for ISM microservices",
        "available_services": list(SERVICE_URLS.keys()),
        "api_prefix": "/api",
        "documentation": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Check health of gateway and all services"""
    services_health = {}
    
    for service_name, service_url in SERVICE_URLS.items():
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{service_url}/health")
                services_health[service_name] = response.json() if response.status_code == 200 else "unhealthy"
        except Exception as e:
            services_health[service_name] = f"error: {str(e)}"
    
    return {
        "gateway": "healthy",
        "services": services_health
    }


# ===== AUTHENTICATION ROUTES =====
@app.post("/api/auth/register")
async def register(user_data: dict):
    """Forward registration request to auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICE_URLS['auth']}/api/auth/register",
            json=user_data
        )
        return response.json()


# dependency used by protected endpoints to resolve current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Call auth service verify endpoint and return user dict."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SERVICE_URLS['auth']}/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return resp.json()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    """Render a role-specific dashboard page for the authenticated user."""
    role = user.get("role")
    context = {"request": request, "user": user}

    # gather some common metrics
    async with httpx.AsyncClient() as client:
        # audit log for dashboard view
        await client.post(
            f"{SERVICE_URLS['auth']}/api/auth/audit-logs",
            json={
                "user_id": user.get("id"),
                "action": "view_dashboard",
                "resource": f"{role}_dashboard",
                "status": "success"
            }
        )

        # fetch user list if admin
        if role == "admin":
            users_resp = await client.get(f"{SERVICE_URLS['auth']}/api/auth/users")
            context["users_count"] = len(users_resp.json()) if users_resp.status_code == 200 else 0
            audit_resp = await client.get(f"{SERVICE_URLS['auth']}/api/auth/audit-logs")
            context["audit_count"] = len(audit_resp.json()) if audit_resp.status_code == 200 else 0
            # also fetch course counts
            courses_resp = await client.get(f"{SERVICE_URLS['curriculum']}/api/curriculum/courses")
            context["course_count"] = len(courses_resp.json()) if courses_resp.status_code == 200 else 0

        elif role == "instructor":
            # show courses taught by this instructor
            courses_resp = await client.get(f"{SERVICE_URLS['curriculum']}/api/curriculum/courses")
            if courses_resp.status_code == 200:
                all_courses = courses_resp.json()
                context["my_courses"] = [c for c in all_courses if c.get("instructor_id") == user.get("id")]
            else:
                context["my_courses"] = []

        elif role == "student":
            # show profile info
            profile_resp = await client.get(f"{SERVICE_URLS['student']}/api/students/{user.get('id')}/profile")
            context["profile"] = profile_resp.json() if profile_resp.status_code == 200 else {}

        elif role == "staff":
            # financial summary
            fin_resp = await client.get(f"{SERVICE_URLS['finance']}/api/finance/reports/summary")
            context["finance_summary"] = fin_resp.json() if fin_resp.status_code == 200 else {}

    template_name = {
        "admin": "admin_dashboard.html",
        "instructor": "instructor_dashboard.html",
        "student": "student_dashboard.html",
        "staff": "staff_dashboard.html"
    }.get(role, None)

    if not template_name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dashboard unavailable for this role")

    return templates.TemplateResponse(template_name, context)


@app.post("/api/auth/login")
async def login(credentials: dict):
    """Forward login request to auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICE_URLS['auth']}/api/auth/login",
            json=credentials
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@app.get("/api/auth/users")
async def get_users():
    """Get all users from auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['auth']}/api/auth/users")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch users")
        return response.json()


@app.get("/api/auth/users/{user_id}")
async def get_user(user_id: int):
    """Get specific user from auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['auth']}/api/auth/users/{user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="User not found")
        return response.json()


@app.get("/api/auth/audit-logs")
async def get_audit_logs(user_id: int = None, action: str = None):
    """Get audit logs from auth service (admin only)"""
    params = {}
    if user_id:
        params["user_id"] = user_id
    if action:
        params["action"] = action
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICE_URLS['auth']}/api/auth/audit-logs",
            params=params
        )
        return response.json()


# ===== STUDENT ROUTES =====
@app.get("/api/students")
async def list_students(skip: int = 0, limit: int = 10):
    """List all students"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICE_URLS['student']}/api/students",
            params={"skip": skip, "limit": limit}
        )
        return response.json()


@app.post("/api/students")
async def create_student(student_data: dict):
    """Create a new student"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICE_URLS['student']}/api/students",
            json=student_data
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Failed to create student")
        return response.json()


@app.get("/api/students/{student_id}")
async def get_student(student_id: int):
    """Get specific student"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['student']}/api/students/{student_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Student not found")
        return response.json()


@app.get("/api/students/{student_id}/profile")
async def get_student_profile(student_id: int):
    """Get student profile with enrollments and grades"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['student']}/api/students/{student_id}/profile")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Student not found")
        return response.json()


@app.put("/api/students/{student_id}")
async def update_student(student_id: int, student_update: dict):
    """Update student information"""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{SERVICE_URLS['student']}/api/students/{student_id}",
            json=student_update
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to update student")
        return response.json()


# ===== CURRICULUM ROUTES =====
@app.get("/api/curriculum/courses")
async def list_courses(skip: int = 0, limit: int = 10):
    """List all courses"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICE_URLS['curriculum']}/api/curriculum/courses",
            params={"skip": skip, "limit": limit}
        )
        return response.json()


@app.post("/api/curriculum/courses")
async def create_course(course_data: dict):
    """Create a new course"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICE_URLS['curriculum']}/api/curriculum/courses",
            json=course_data
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Failed to create course")
        return response.json()


@app.get("/api/curriculum/courses/{course_id}")
async def get_course(course_id: int):
    """Get specific course"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['curriculum']}/api/curriculum/courses/{course_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Course not found")
        return response.json()


@app.get("/api/curriculums")
async def list_curriculums():
    """List all curriculums"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['curriculum']}/api/curriculum/curriculums")
        return response.json()


# ===== FINANCE ROUTES =====
@app.get("/api/finance/accounts/{student_id}")
async def get_student_account(student_id: int):
    """Get student financial account"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['finance']}/api/finance/accounts/{student_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Account not found")
        return response.json()


@app.get("/api/finance/invoices")
async def list_invoices(student_id: int = None, skip: int = 0, limit: int = 10):
    """List invoices"""
    params = {"skip": skip, "limit": limit}
    if student_id:
        params["student_id"] = student_id
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICE_URLS['finance']}/api/finance/invoices",
            params=params
        )
        return response.json()


@app.post("/api/finance/invoices")
async def create_invoice(invoice_data: dict):
    """Create an invoice"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICE_URLS['finance']}/api/finance/invoices",
            json=invoice_data
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Failed to create invoice")
        return response.json()


@app.get("/api/finance/reports/summary")
async def get_financial_summary():
    """Get financial summary report"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['finance']}/api/finance/reports/summary")
        return response.json()


# ===== NOTIFICATION ROUTES =====
@app.get("/api/notifications")
async def list_notifications(user_id: int = None, unread_only: bool = False, skip: int = 0, limit: int = 10):
    """List notifications"""
    params = {"skip": skip, "limit": limit, "unread_only": unread_only}
    if user_id:
        params["user_id"] = user_id
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICE_URLS['notification']}/api/notifications",
            params=params
        )
        return response.json()


@app.post("/api/notifications")
async def send_notification(notification_data: dict):
    """Send a notification"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICE_URLS['notification']}/api/notifications",
            json=notification_data
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Failed to send notification")
        return response.json()


# ===== STAFF ROUTES =====
@app.get("/api/staff")
async def list_staff(skip: int = 0, limit: int = 10):
    """List all staff members"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICE_URLS['staff']}/api/staff",
            params={"skip": skip, "limit": limit}
        )
        return response.json()


@app.post("/api/staff")
async def create_staff(staff_data: dict):
    """Create a new staff member"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICE_URLS['staff']}/api/staff",
            json=staff_data
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Failed to create staff")
        return response.json()


@app.get("/api/staff/{staff_id}")
async def get_staff(staff_id: int):
    """Get specific staff member"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['staff']}/api/staff/{staff_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Staff not found")
        return response.json()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

