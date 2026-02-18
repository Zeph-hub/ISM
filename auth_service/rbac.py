from fastapi import Depends, HTTPException
from auth import decode_token

def role_required(required_role: str):
    def wrapper(token: str = Depends()):
        payload = decode_token(token)
        if payload["role"] != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return payload
    return wrapper
