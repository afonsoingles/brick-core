from pymongo import MongoClient
from redis import Redis
import os 


class Database:
    def __init__(self):
        self._mongo_