from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    return {"service" : "Notification Service", "status": "running"}



# def main():
#     print("Hello from notification-service!")


# if __name__ == "__main__":
#     main()
