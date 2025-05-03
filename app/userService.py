from app.db import users
from bson import ObjectId

def get_user_profile(user_id: str):
    user_data = users.find_one({"_id": ObjectId(user_id)},{"_id": 0, "password": 0})  
    return user_data
