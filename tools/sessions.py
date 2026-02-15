from utils.database import Database
import jwt
import uuid
import datetime
import os


class SessionsController:
    def __init__(self):
        self.db = Database()
        self.jwt_secret = os.environ.get("JWT_SECRET")
    
    def create_session(self, user) -> str:
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        payload = {
            "iss": "brick-core",
            "sub": user,
            "exp": now + 604800, # 7 days
            "iat": now,
            "jti": str(uuid.uuid4())
        }

        token = jwt.encode(
            payload,
            self.jwt_secret,
            algorithm="HS256"
        )

        self.db.redis.set(f"users.sessions.{token}", "valid", ex=604800)

        return token
    
    def is_valid_session(self, token) -> bool:
        # this isn't meant to validate the jwt.
        # it just checks if the token wasn't revoked for some reason (eg: logout)

        return self.db.redis.get(f"users.sessions.{token}") == "valid"
    
    def revoke_session(self, token) -> None:
        self.db.redis.delete(f"users.sessions.{token}")
        return