from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    # return {"message": "Welcome to the Curriculum Service!"}
    return {"service" : "Curriculum Service", "status": "running"}