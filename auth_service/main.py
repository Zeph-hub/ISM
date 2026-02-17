from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .routes import router

app = FastAPI(
    title="Auth Service",
    description="Authentication, Authorization, and Accounting Service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "auth-service",
        "version": "1.0.0",
        "description": "Authentication, Authorization, and Accounting Service",
        "endpoints": {
            "authentication": ["/api/auth/register", "/api/auth/login", "/api/auth/refresh"],
            "authorization": ["/api/auth/users", "/api/auth/users/{user_id}/role"],
            "accounting": ["/api/auth/audit-logs"]
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
