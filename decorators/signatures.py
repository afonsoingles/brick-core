from functools import wraps
from fastapi import Request, HTTPException
from utils.signatures import verify_signature

def valid_signature(func):
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

        body = await request.body()
        signature = request.headers.get("X-Signature", "")
        timestamp = request.headers.get("X-Timestamp", "")

        if not verify_signature(body, signature, timestamp):
            raise HTTPException(status_code=401, detail="Invalid signature")

        return await func(*args, **kwargs)
    return wrapper