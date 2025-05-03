
from pymongo import MongoClient
from config import MONGO_URI
from fastapi.security import HTTPBearer

client = MongoClient(MONGO_URI)
db = client["authdb"]
users = db["users"]
security = HTTPBearer()
