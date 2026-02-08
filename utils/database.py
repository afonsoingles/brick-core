from pymongo import MongoClient
from redis import Redis
import os 


class Database:
    _mongo_client = None
    _redis_client = None

    def __init__(self):
        if not Database._mongo_client:
            if os.environ.get("MONGO_FORCE_DB_NAME"):
                name = os.environ.get("MONGO_FORCE_DB_NAME")
            else:
                name = "brick_" + os.environ.get("APP_ENV", "APP_ENVIRONMENT")
            
            Database._mongo_client = MongoClient( os.environ.get("MONGO_URL"))
        
        if not Database._redis_client:
            Database._redis_client = Redis.from_url(
                os.environ.get("REDIS_URL"),
                decode_responses=True
            )

        self.redis = Database._redis_client
        self.mongo = Database._mongo_client[name] 