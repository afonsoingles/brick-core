import os
from functools import wraps
from fastapi import Request, HTTPException

def valid_secure_key(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is None:
            raise ValueError("Request object not found in function arguments.")

        secure_key = request.headers.get("X-Secure-Key", "")
        expected_key = os.environ.get("SECURE_KEY", "")

        if secure_key != expected_key:
            raise HTTPException(status_code=401, detail="Invalid secure key")

        return await func(*args, **kwargs)
    return wrapper
