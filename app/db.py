
from pymongo import MongoClient
from config import MONGO_URI
from fastapi.security import HTTPBearer

client = MongoClient(MONGO_URI)
db = client["authdb"] #Change this DB Name
users = db["users"]
pattern = db["pattern"] #Find a way to get this DB created with data always when spinnedup
security = HTTPBearer()
