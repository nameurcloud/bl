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
        token = request.headers.get('X-App-Auth')
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
    found = users.find_one({"email": user.email})
    if not found or not verify_password(user.password, found["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token(str(found["email"]))
    return {"token": token}

insider_router = APIRouter(
    prefix="/insider",
    dependencies=[Depends(get_current_user)] 
)


@insider_router.get("/api")
def insider_api():
    return {"message": "api"}

@insider_router.get("/config")
def insider_config():
    return {"message": "config"}

@insider_router.get("/dashboard")
def insider_dashboard():
    return {"message": "dashboard"}

@insider_router.get("/faq")
def insider_faq():
    return {"message": "faq"}

@insider_router.get("/names")
def insider_names():
    return {"message": "names"}

@insider_router.get("/payment")
def insider_payment():
    return {"settings": "payment"}

@insider_router.get("/recom")
def insider_recom():
    return {"message": "recom"}

@insider_router.get("/support")
def insider_support():
    return {"message": "support"}

