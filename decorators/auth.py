from functools import wraps
from fastapi import Request, HTTPException
import jwt
import os
from tools.sessions import SessionsController
from tools.users import UserTools

def require_auth(func=None, *, return_safe_user=True, require_admin=False):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            session_controller = SessionsController()
            user_tools = UserTools()
            jwt_secret = os.environ.get("JWT_SECRET")

            request = kwargs.get("request", None)
            if request is None:
                for a in args:
                    if isinstance(a, Request):
                        request = a
                        break

            auth_token = None
            if request is not None:
                auth_token = request.headers.get("Authorization", None)

            if auth_token is None or not auth_token.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Unauthorized")

            auth_token = auth_token.split(" ")[1]

            try:
                payload = jwt.decode(auth_token, jwt_secret, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")
            except:
                print("something went wrong here!")
                raise HTTPException(status_code=401, detail="Invalid token")

            if not session_controller.is_valid_session(auth_token):
                raise HTTPException(status_code=401, detail="Invalid session")

            
            user = user_tools.get_user_by_id(payload["sub"], return_safe_user)

            if user == "not_found":
                raise HTTPException(status_code=404, detail="User not found")

            if user["suspended"]:
                raise HTTPException(status_code=403, detail="User suspended")
            
            if not user["admin"] and require_admin:
                raise HTTPException(status_code=403, detail="Admin required")

            request.state.user = user

            return await fn(*args, **kwargs)
        return wrapper

    if callable(func):
        return decorator(func)
    return decorator