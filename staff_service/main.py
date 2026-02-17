from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .routes import router

app = FastAPI(
    title="Staff Service",
    description="Staff Management Service",
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
        "service": "staff-service",
        "version": "1.0.0",
        "description": "Staff Management Service",
        "endpoints": {
            "staff": ["/api/staff", "/api/staff/{staff_id}"],
            "departments": ["/api/staff/departments"],
            "salary": ["/api/staff/{staff_id}/salary"],
            "absences": ["/api/staff/{staff_id}/absences"]
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "staff-service"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
