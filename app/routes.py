from fastapi import APIRouter, HTTPException , Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import UserIn, UserLogIn
from app.auth import hash_password, verify_password, create_token , decode_token
from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI

router = APIRouter(prefix="")
client = MongoClient(MONGO_URI)
db = client["authdb"]
users = db["users"]
security = HTTPBearer()

async def get_current_user(request: Request):
    try:
        body = await request.json()
        token = body.get('token')
        if not token:
            raise HTTPException(status_code=401, detail="Token missing")
        # decode and return user id (or whatever decode_token returns)
        return decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
def register(user: UserIn):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = hash_password(user.password)
    result = users.insert_one({"email": user.email, "password": hashed_pw, "fname": user.fname, "lname": user.lname , "mobile":user.mobile, "dob":user.dob, "plan": user.plan})
    return {"id": str(result.inserted_id), "email": user.email}

@router.post("/login")
def login(user: UserLogIn):
    print('Login backend')
    print(user)
    found = users.find_one({"email": user.email})
    if not found or not verify_password(user.password, found["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token(str(found["_id"]))
    return {"token": token, "user": {"id": str(found["_id"]), "email": found["email"]}}

insider_router = APIRouter(
    prefix="/insider",
    dependencies=[Depends(get_current_user)] 
)

@insider_router.get("/api")
def dashboard_home():
    return {"message": "Welcome"}

@insider_router.get("/config")
def dashboard_stats():
    return {"message": "Welcome"}

@insider_router.get("/dashboard")
def dashboard_settings():
    return {"message": "Welcome"}

@insider_router.get("/faq")
def dashboard_home():
    return {"message": "Welcome"}

@insider_router.get("/names")
def dashboard_stats():
    return {"message": "Welcome"}

@insider_router.get("/payment")
def dashboard_settings():
    return {"settings": "Welcome"}

@insider_router.get("/recom")
def dashboard_home():
    return {"message": "Welcome"}

@insider_router.get("/support")
def dashboard_stats():
    return {"message": "Welcome"}

