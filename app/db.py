import os
from typing import Dict, Any
from bson import ObjectId
import motor.motor_asyncio
from pymongo import ASCENDING

MONGO_URL = os.getenv("MONGODB_URL")
MONGO_DB = os.getenv("MONGO_DB")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
users = db.get_collection("users")


async def init_indexes() -> None:
    await users.create_index("email",unique=True)
    await users.create_index([("name",ASCENDING)])

def oid(id_str: str) -> ObjectId:
    return ObjectId(id_str)

def doc_to_user_out(doc: Dict[str,Any]) -> Dict[str,Any]:
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "email": doc["email"],
        "age": doc["age"],
        "is_active": doc.get("is_active",True)
    }
