from fastapi import Query
from fastapi import APIRouter, HTTPException , Depends, Request
from app.models import ConfigBody, GeneratedName, UserIn, UserLogIn, apiKey
from app.auth import hash_password, verify_password, create_token , decode_token
from bson import ObjectId
from app.db import users , client, pattern
from app.config import get_user_pattern_config , set_user_pattern_config
from app.userService import get_user_plan, get_user_profile
from app.names import get_name, set_name
from app.api import setApiKey , getApiKeys
from app.dashboard import getCSPCount, getCSPResRegCount, getNameCount , getModeCount

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

@router.post("/apkey")
def apkey(key : apiKey,user_id=Depends(get_current_user)):
    status = setApiKey(user_id,key)
    return {"status": status}

@router.get("/apkey")
def apkey(user_id=Depends(get_current_user)):
    keys = getApiKeys(user_id)
    return {"keys": keys}



@router.delete("/apkey")
def delete_api_key(partial_key: str = Query(...), email: str = Query(...), user_id=Depends(get_current_user)):
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})
    if not user_org or "org" not in user_org:
        raise HTTPException(status_code=404, detail="Organization not found")

    configdb = client[user_org["org"]]
    apiTable = configdb["api"]

    result = apiTable.delete_one({"partialKey": partial_key, "email": email})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"status": "Deleted"}



@router.get("/config")
def config(user_id=Depends(get_current_user)):
    patter_config = get_user_pattern_config(user_id)
    return {"pattern_config": patter_config}

@router.post("/config")
def config(updated_config: ConfigBody,user_id=Depends(get_current_user)):
    result = set_user_pattern_config(user_id,updated_config)
    return {"result": result}


@router.get("/dashboard")
def dashboard(user_id=Depends(get_current_user)):
    nameCount = getNameCount(user_id)
    modecount = getModeCount(user_id)
    cspcount = getCSPCount(user_id)
    cspresregCount = getCSPResRegCount(user_id)
    retunObj = {
        "generatedNameCount" : nameCount,
        "modeCount" : modecount,
        "cspCount" : cspcount,
        "cspResRegCount" : cspresregCount
    }
    return retunObj

@insider_router.get("/faq")
def faq():
    return {"message": "Welcome"}

@router.get("/names")
def names(user_id=Depends(get_current_user)):
    pattern_config = get_user_pattern_config(user_id)
    return {"pattern_config": pattern_config}

@router.post("/name")
def name(name : GeneratedName,user_id=Depends(get_current_user)):
    ret_status = set_name(user_id,name)
    return {"status": ret_status}

@router.get("/name")
def name(user_id=Depends(get_current_user)):
    allnames = get_name(user_id)
    return {"result": allnames}

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



