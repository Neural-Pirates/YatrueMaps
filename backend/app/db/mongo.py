from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends


class MongoDB:
    client: AsyncIOMotorClient = None

    @classmethod
    async def connect(cls, uri: str):
        cls.client = AsyncIOMotorClient(uri)
        print("Connected to MongoDB")

    @classmethod
    async def close(cls):
        cls.client.close()
        print("Disconnected from MongoDB")

    @classmethod
    def get_database(cls, db_name: str):
        return cls.client[db_name]


# Dependency for injecting database
def get_database(db_name: str = "YatrueMaps"):
    db = MongoDB.get_database(db_name)
    return db
