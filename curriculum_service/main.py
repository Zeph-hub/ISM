from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import init_db
from .routes import router

# Initialize database tables
init_db()

app = FastAPI(
    title="Curriculum Service",
    description="Course and Curriculum Management Service",
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
        "service": "curriculum-service",
        "version": "1.0.0",
        "description": "Course and Curriculum Management Service",
        "endpoints": {
            "courses": ["/api/curriculum/courses", "/api/curriculum/courses/{course_id}"],
            "modules": ["/api/curriculum/courses/{course_id}/modules"],
            "assignments": ["/api/curriculum/courses/{course_id}/assignments"],
            "curriculums": ["/api/curriculum/curriculums"]
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "curriculum-service"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)