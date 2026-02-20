from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import router

app = FastAPI(
    title="Notification Service",
    description="Notification Management Service",
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
        "service": "notification-service",
        "version": "1.0.0",
        "description": "Notification Management Service",
        "endpoints": {
            "notifications": ["/api/notifications"],
            "templates": ["/api/notifications/templates"],
            "preferences": ["/api/notifications/preferences/{user_id}"],
            "bulk": ["/api/notifications/bulk"]
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
