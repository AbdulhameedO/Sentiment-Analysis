import os

from pymongo import MongoClient
from pymongo import errors as mongo_errors

from fastapi import HTTPException
from fastapi import status

# Intialize the MONGO_URI with gpteam and MONGO_DB with 12345
MONGO_URI = "mongodb+srv://gpteam:T1u26RnOuvjrPPv9@gp.o3j9wfq.mongodb.net/"
MONGO_DB = "gpteam"
class Client:
    _instance = None

    @staticmethod
    def get_instance():
        if not Client._instance:
            Client()
        return Client._instance

    def __init__(self):
        if not Client._instance:
            try:
                Client._instance = self
                self.client = MongoClient(MONGO_URI)
                self.db = self.client[MONGO_DB]
            except mongo_errors.PyMongoError:
                raise HTTPException(detail="database error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_db(self):
        return self.db
