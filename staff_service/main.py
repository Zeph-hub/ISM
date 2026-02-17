from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    return {"service" : "Staff Service", "status": "running"}


# def main():
#     print("Hello from staff-service!")


# if __name__ == "__main__":
#     main()
