from app.db import users

def get_user_profile(email: str):
    user_data = users.find_one({"email": email},{"_id": 0, "password": 0})  
    if user_data:
        user = user_data
    return user
