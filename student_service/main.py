from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import init_db
from routes import router

# Initialize database tables
init_db()

app = FastAPI(
    title="Student Service",
    description="Student Management Service",
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
        "service": "student-service",
        "version": "1.0.0",
        "description": "Student Management Service",
        "endpoints": {
            "students": ["/api/students", "/api/students/{student_id}"],
            "enrollments": ["/api/students/{student_id}/enroll", "/api/students/{student_id}/enrollments"],
            "grades": ["/api/students/{student_id}/grades", "/api/students/{student_id}/gpa"]
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "student-service"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)