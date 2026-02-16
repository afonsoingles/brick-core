from utils.database import Database
import uuid
import bcrypt
import json
import datetime

class UserTools:
    def __init__(self):
        self.db = Database()
        pass
    
    def _hash_password(self, password):
        salt = bcrypt.gensalt(rounds=12)
        result = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        return result
    
    def verify_password_hash(self, password, hashed):
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    
    def create_user(self, name, email, password, region, language, auth_methods=[]):
        
        exists_redis = self.db.redis.get(f"users.lookup.email:{email}")
        if exists_redis:
            return "email_already_registered"
        
        exists_mongo = self.db.mongo.users.find_one({"email": email})
        if exists_mongo:
            return "email_already_registered"
        
        hashed_password = self._hash_password(password)
        id = str(uuid.uuid4())
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()

        user = {
            "_id": id, # MongoDB is annoying with ts.
            "id": id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "auth_methods": auth_methods,
            "region": region,
            "language": language,
            "superadmin": False,
            "admin": False,
            "permissions": [],
            "suspended": False,
            "created_at": now_ts,
            "updated_at": now_ts
        }

        self.db.mongo.users.insert_one(user)

        self.db.redis.set(f"users.user:{id}", json.dumps(user), ex=10800)
        self.db.redis.set(f"users.lookup.email:{email}", id, ex=10800)

        return "user_created"
    
    def get_user_by_id(self, id, safe=True):
        
        redis_user = self.db.redis.get(f"users.user:{id}")
        if redis_user:
            real_user = json.loads(redis_user)

        if not redis_user:
            real_user = self.db.mongo.users.find_one({"id": id})

        if not real_user:
            return "not_found"
        

        if not redis_user:
            # If the user is not cached, cache it for future requests (3h)

            self.db.redis.set(f"users.user:{id}", json.dumps(real_user), ex=10800)
            self.db.redis.set(f"users.lookup.email:{real_user['email']}", id, ex=10800)
        

        if safe:
            del real_user["password"]
        
        if "_id" in real_user:
            del real_user["_id"]

        return real_user

    def get_user_by_email(self, email, safe=True):
        #TODO: There should be a better way to do this (Don't repeat yourself)
        
        redis_id = self.db.redis.get(f"users.lookup.email:{email}")
        if redis_id:
            return self.get_user_by_id(redis_id, safe=safe)
        
        real_user = self.db.mongo.users.find_one({"email": email})
        if not real_user:
            return "not_found"
        
        # Cache the user for future requests (3h)
        self.db.redis.set(f"users.user:{real_user['id']}", json.dumps(real_user), ex=10800)
        self.db.redis.set(f"users.lookup.email:{email}", real_user["id"], ex=10800)

        if safe:
            del real_user["password"]
        
        del real_user["_id"]

        return real_user