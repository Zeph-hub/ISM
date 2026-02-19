from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt, datetime

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    password: str
    role: str

# Mock user store (replace with DB)
users = {
    "admin": {"password": "hashed_admin_pw", "role": "admin"},
    "teacher": {"password": "hashed_teacher_pw", "role": "teacher"},
}

def create_token(username: str, role: str):
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login(user: User):
    if user.username in users and users[user.username]["password"] == user.password:
        token = create_token(user.username, users[user.username]["role"])
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
