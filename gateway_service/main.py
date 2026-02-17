from fastapi import FastAPI
import httpx

app = FastAPI()
@app.get("/auth")
async def get_users():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/users")
        return response.json()

@app.get("/curriculums")
async def get_curriculums():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8002/curriculums")
        return response.json()
    
@app.get("/notifications")
async def get_notifications():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8003/notifications")
        return response.json()
    
@app.get("/finance")
async def get_finance():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8004/finance")
        return response.json()

@app.get("/students")
async def get_students():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8005/students")
        return response.json()

@app.get("/staff")
async def get_staff():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8006/staff")
        return response.json()

