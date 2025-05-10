from typing import Dict, List
from fastapi import APIRouter, Body, HTTPException , Depends, Request
from fastapi.security import  HTTPAuthorizationCredentials
from app.models import ConfigBody, UserIn, UserLogIn
from app.auth import hash_password, verify_password, create_token , decode_token
from bson import ObjectId
from app.db import users , client, pattern
from app.config import get_user_pattern_config , set_user_pattern_config
from app.userService import get_user_plan, get_user_profile

router = APIRouter(prefix="")

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
    # Check if user or org already exists
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    if users.find_one({"org": user.org}):
        raise HTTPException(status_code=401, detail="Organization already taken")

    # Hash the password and create user
    hashed_pw = hash_password(user.password)
    user_data = {
        "email": user.email,
        "password": hashed_pw,
        "fname": user.fname,
        "lname": user.lname,
        "mobile": user.mobile,
        "dob": user.dob,
        "plan": user.plan,
        "org": user.org
    }
    result = users.insert_one(user_data)

    # Step 1: Create new DB named after the organization
    org_db = client[user.org]  # dynamically select the DB

    # Step 2: Create 'pattern' collection inside that DB
    pattern_collection = org_db["pattern"]

    # Step 3: Copy all users to the new collection
    patterns = list(pattern.find({}))  # exclude _id to avoid conflict
    if patterns:
        pattern_collection.insert_many(patterns)

    return {"id": str(result.inserted_id), "email": user.email}

@router.post("/login")
def login(user: UserLogIn):
    found = users.find_one({"email": user.email})
    if not found or not verify_password(user.password, found["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token(str(found["_id"]))
    return {"token": token, "user": {"id": str(found["_id"]), "email": found["email"]}}

@router.get("/auth-check") #Checks authencity of Token
def authCheck(user_id=Depends(get_current_user)):
    return {"status": "ok", "user_id": user_id}

insider_router = APIRouter(
    prefix="/insider",
    dependencies=[Depends(get_current_user)] 
)

@insider_router.get("/api")
def api():
    return {"message": "Welcome"}

@router.get("/config")
def config(user_id=Depends(get_current_user)):
    patter_config = get_user_pattern_config(user_id)
    return {"pattern_config": patter_config}

@router.post("/config")
def config(updated_config: ConfigBody,user_id=Depends(get_current_user)):
    result = set_user_pattern_config(user_id,updated_config)
    return {"result": result}

@insider_router.get("/dashboard")
def dashboard():
    return {"message": "Welcome"}

@insider_router.get("/faq")
def faq():
    return {"message": "Welcome"}

@insider_router.get("/names")
def names():
    return {"message": "Welcome"}

@insider_router.get("/payment")
def payment():
    return {"settings": "Welcome"}

@insider_router.get("/recom")
def recom():
    return {"message": "Welcome"}

@insider_router.get("/support")
def support():
    return {"message": "Welcome"}

@router.get("/profile")
def profile(user_id=Depends(get_current_user)):
    userProfile = get_user_profile(user_id)
    return {"profile": userProfile}

@router.get("/plan")
def profile(user_id=Depends(get_current_user)):
    userPlan = get_user_plan(user_id)
    return {"userPlan": userPlan}



