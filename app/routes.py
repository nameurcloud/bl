from fastapi import Query
from fastapi import APIRouter, HTTPException , Depends, Request
from app.models import ApiPayload,ConfigBody, GeneratedName, PaymentRequest, PaymentVerificationRequest, UserIn, UserLogIn, apiKey , APIKeyRequest
from app.auth import hash_password, verify_password, create_token , decode_token
from bson import ObjectId
from app.db import users , client, pattern
from app.config import get_user_pattern_config , set_user_pattern_config
from app.userService import get_user_plan, get_user_profile
from app.names import get_name, get_name_api, set_name, set_name_api
from app.api import check_org, check_orgapi_map, check_permission, get_email_api, setApiKey , getApiKeys, validate_key
from app.dashboard import getCSPCount, getCSPResRegCount, getNameCount , getModeCount
from app.payment import set_payment, set_payment_order
from config import JWT_SECRET
import jwt
from datetime import datetime
import razorpay
import hmac
import hashlib

RAZORPAY_KEY_ID = "rzp_test_0XHm0CZsK9Odpf"
RAZORPAY_SECRET = "Zn6ppQ1H92riBDlpBFVri0Pa"

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))

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

@router.post("/genapkey")
def genapikey(data: APIKeyRequest):
    print("Received request:", data)
    try:
        expiry_dt = datetime.fromisoformat(data.expiry.replace("Z", "+00:00"))
    except Exception:
        return {"error": "Invalid expiry datetime format"}

    payload = {
        "email": data.email,
        "expiry": data.expiry,
        "permissions": data.permissions,
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return {"apiKey": token}


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

@router.post("/create-razorpay-order")
async def create_razorpay_order(payment: PaymentRequest,user_id=Depends(get_current_user)):
    
    try:
        order = razorpay_client.order.create({
            "amount": payment.amount,
            "currency": "INR",
            "receipt": f"receipt_{int(__import__('time').time())}",
            "payment_capture": 1,
        })
        set_payment_order(user_id,order)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Razorpay order: {str(e)}")

@router.post("/verify-razorpay-payment")
async def verify_payment(payload: PaymentVerificationRequest,user_id=Depends(get_current_user)):
    try:
        generated_signature = hmac.new(
            RAZORPAY_SECRET.encode(),
            f"{payload.razorpay_order_id}|{payload.razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != payload.razorpay_signature:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Optional: fetch payment status from Razorpay
        payment_info = razorpay_client.payment.fetch(payload.razorpay_payment_id)
        set_payment(user_id,payment_info)
        return {
            "status": payment_info["status"],  # can be 'captured', 'failed', etc.
            "method": payment_info["method"],
            "email": payment_info.get("email"),
            "amount": payment_info["amount"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/apy/view")
async def apy_view(payloadIn: ApiPayload):
    full_path = payloadIn.path
    api_key = payloadIn.key
    payload = validate_key(api_key)
    org = full_path.split("/")[1]

    if not api_key or not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")

    if not check_org(org):
        raise HTTPException(status_code=400, detail="Invalid Organization")
    
    if not check_orgapi_map(org,api_key):
        raise HTTPException(status_code=403, detail="API Key not Mapped with Organization")

    if not check_permission(payload, full_path, payloadIn.method):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {
        "action": full_path.split("/")[2],
        "output" : get_name_api(org)
        }

@router.post("/apy/generate")
async def apy_generate(payloadIn: ApiPayload):
    body = payloadIn.body
    full_path = payloadIn.path
    api_key = payloadIn.key
    payload = validate_key(api_key)
    org = full_path.split("/")[1]

    if not api_key or not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")

    if not check_org(org):
        raise HTTPException(status_code=400, detail="Invalid Organization")
    
    if not check_orgapi_map(org,api_key):
        raise HTTPException(status_code=403, detail="API Key not Mapped with Organization")

    if not check_permission(payload, full_path, payloadIn.method):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if not body or not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="Missing or invalid 'body' field")

    pattern = body.get("pattern")
    if not pattern or not isinstance(pattern, str) or pattern.strip() == "":
        raise HTTPException(status_code=422, detail="'pattern' must be a non-empty string")
 
    
    return {
        "action": full_path.split("/")[2],
        "output" : set_name_api(org,pattern,get_email_api(api_key))
        }



