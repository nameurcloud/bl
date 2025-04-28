from fastapi import APIRouter, HTTPException , Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import UserIn, UserLogIn
from app.auth import hash_password, verify_password, create_token , decode_token
from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI

router = APIRouter(prefix="/api")
client = MongoClient(MONGO_URI)
db = client["authdb"]
users = db["users"]
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return decode_token(token)

@router.post("/register")
def register(user: UserIn):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = hash_password(user.password)
    result = users.insert_one({"email": user.email, "password": hashed_pw, "fname": user.fname, "lname": user.lname , "mobile":user.mobile, "dob":user.dob})
    return {"id": str(result.inserted_id), "email": user.email}

@router.post("/login")
def login(user: UserLogIn):
    print("Login route")
    found = users.find_one({"email": user.email})
    if not found or not verify_password(user.password, found["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token(str(found["_id"]))
    return {"token": token, "user": {"id": str(found["_id"]), "email": found["email"]}}

@router.get("/dashboard")
def dashboard(current_user: str = Depends(get_current_user)):
    user_data = users.find_one({"_id": ObjectId(current_user)})

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Welcome!",
        "user": {
            "id": str(user_data["_id"]),
            "email": user_data["email"],
            "fname": user_data["fname"],
            "lname": user_data["lname"]
        }
    }
