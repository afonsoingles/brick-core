from utils.database import Database
import random
import uuid


class LoginCodes:
    def __init__(self):
        self.db = Database()
        pass
    
    def _is_rate_limited(self, id) -> bool:
        attempts = self.db.redis.smembers(f"users.otp.{id}")
        if len(attempts) >= 3:
            return True
        
        return False
        
    def generate_otp(self, user_id):
        if self._is_rate_limited(user_id):
            return "rate_limited"
        
        attempt_id = str(uuid.uuid4())
        random_code = str(random.randint(100000, 999999))

        self.db.redis.set(f"users.otp.attempts.{attempt_id}", random_code, ex=300)
        self.db.redis.set(f"users.otp.attempts.{attempt_id}:user", user_id, ex=300)

        self.db.redis.sadd(f"users.otp.{user_id}", attempt_id)
        self.db.redis.expire(f"users.otp.{user_id}", 300)

        return attempt_id, random_code

    def verify_otp(self, attempt_id, code):
        stored_code = self.db.redis.get(f"users.otp.attempts.{attempt_id}")

        if stored_code is None:
            return False

        if stored_code == code:
            user_id = self.db.redis.get(f"users.otp.attempts.{attempt_id}:user")

            self.db.redis.delete(f"users.otp.attempts.{attempt_id}")
            self.db.redis.delete(f"users.otp.attempts.{attempt_id}:user")

            return user_id

        return "invalid_code"