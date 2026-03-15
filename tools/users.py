from utils.database import Database
from models.user import User, SafeUser
import uuid
import bcrypt
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

        user = User(
            id=id,
            name=name,
            email=email,
            password=hashed_password,
            auth_methods=auth_methods,
            region=region,
            language=language,
            created_at=now_ts,
            updated_at=now_ts,
        )

        user_dict = user.model_dump()
        user_dict["_id"] = id  # MongoDB requires _id

        self.db.mongo.users.insert_one(user_dict)

        self.db.redis.set(f"users.user:{id}", user.model_dump_json(), ex=10800)
        self.db.redis.set(f"users.lookup.email:{email}", id, ex=10800)

        return "user_created"

    def _get_user_model(self, id) -> User | None:
        """Internal helper: returns the full User model (with password) or None."""
        redis_user = self.db.redis.get(f"users.user:{id}")
        if redis_user:
            return User.model_validate_json(redis_user)

        raw = self.db.mongo.users.find_one({"id": id})
        if not raw:
            return None
        user = User.model_validate(raw)
        # Cache for future requests (3h)
        self.db.redis.set(f"users.user:{id}", user.model_dump_json(), ex=10800)
        self.db.redis.set(f"users.lookup.email:{user.email}", id, ex=10800)
        return user
    
    def get_user_by_id(self, id, safe=True) -> User | SafeUser | str:
        user = self._get_user_model(id)
        if user is None:
            return "not_found"
        if safe:
            return SafeUser.model_validate(user.model_dump(exclude={"password"}))
        return user

    def get_user_by_email(self, email, safe=True) -> User | SafeUser | str:
        #TODO: There should be a better way to do this (Don't repeat yourself)
        
        redis_id = self.db.redis.get(f"users.lookup.email:{email}")
        if redis_id:
            return self.get_user_by_id(redis_id, safe=safe)
        
        raw = self.db.mongo.users.find_one({"email": email})
        if not raw:
            return "not_found"
        
        user = User.model_validate(raw)
        # Cache for future requests (3h)
        self.db.redis.set(f"users.user:{user.id}", user.model_dump_json(), ex=10800)
        self.db.redis.set(f"users.lookup.email:{email}", user.id, ex=10800)

        if safe:
            return SafeUser.model_validate(user.model_dump(exclude={"password"}))
        return user
    
    def update_user(self, id, data):
        user = self._get_user_model(id)

        if user is None:
            return "not_found"
        
        user_dict = user.model_dump()
        for key in data:
            if key not in ["suspended", "permissions", "admin", "superadmin", "password", "email", "created_at", "updated_at", "id"]:
                user_dict[key] = data[key]
            else:
                return "protected_field"
        
        user_dict["updated_at"] = datetime.datetime.now(datetime.timezone.utc).timestamp()

        user = User.model_validate(user_dict)
        updated_dict = user.model_dump()

        self.db.mongo.users.update_one({"id": id}, {"$set": updated_dict})
        self.db.redis.set(f"users.user:{id}", user.model_dump_json(), ex=10800)
        self.db.redis.set(f"users.lookup.email:{user.email}", id, ex=10800)
        return "user_updated"