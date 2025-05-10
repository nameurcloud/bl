from app.db import users
from bson import ObjectId

def get_user_profile(user_id: str):
    user_data = users.find_one({"_id": ObjectId(user_id)},{"_id": 0, "password": 0})  
    return user_data


def get_user_plan(user_id: str):
    user_plan = users.find_one({"_id": ObjectId(user_id)},{"plan": 1})
    if user_plan and "_id" in user_plan:
        del user_plan["_id"] 
    return user_plan