import os
from pymongo import MongoClient



class MongoDB:
    _initiated = None
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_CON'))
        self.database = self.client.discord
    def get_collection(self,collection):
        return self.database[collection]


def MongoInit():
    if MongoDB._initiated is None:
        MongoDB._initiated = MongoDB()
    return MongoDB._initiated
