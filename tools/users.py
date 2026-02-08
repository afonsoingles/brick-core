from utils.database import Database
import uuid
import bcrypt
import json

class UserTools:
    def __init__(self):
        self.db = Database()
        pass
    
    def _hash_password(self, password):
        salt = bcrypt.gensalt(rounds=12)
        result = bcrypt.hashpw(password, salt).decode("utf-8")

        return result
    
    def create_user(self, name, email, password, region, language):
        
        exists_redis = self.db.redis.get(f"users.lookup.email:{email}")
        if exists_redis:
            return "email_already_registered"
        
        exists_mongo = self.db.mongo.users.find_one({"email": email})
        if exists_mongo:
            return "email_already_registered"
        
        hashed_password = self._hash_password(password)
        id = str(uuid.uuid4())

        user = {
            "id": id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "region": region,
            "language": language
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