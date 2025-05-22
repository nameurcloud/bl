from app.db import client, users
from bson import ObjectId
from app.models import apiKey
# app/auth.py
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime , timezone
from config import JWT_SECRET  # make sure this matches where you store your secret

def validate_key(api_key: str) -> dict | None:
    try:
        token = api_key.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Optional: check expiry field manually if not using `exp` claim
        expiry_str = payload.get("expiry")
        if expiry_str:
            expiry_dt = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            if expiry_dt < datetime.now(timezone.utc):
                print("Token expired")
                return None

        return payload
    except ExpiredSignatureError:
        print("Token expired")
        return None
    except InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None


# app/auth.py
def check_permission(payload: dict, path: str, method: str) -> bool:
    permissions = payload.get("permissions", [])
    # Strict method-to-permission mapping
    if method == "POST" and path.split("/")[2] == "delete":
        return "delete" in permissions
    if method in ["GET"] and path.split("/")[2] == "view":
        return "view" in permissions
    if method in ["POST"] and path.split("/")[2] == "generate":
        return "generate" in permissions

    # Default: deny unknown methods
    return False

def setApiKey(user_id: str, key: apiKey):
    # Get the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Use the user's org-specific database
    configdb = client[user_org["org"]]
    apiTable = configdb["api"]

    key_dict = key.model_dump()  # or key.dict() if using older Pydantic version
    key_dict["id"] = str(key_dict["id"])


    insert_result = apiTable.insert_one(key_dict)

    if insert_result.acknowledged :
        return "Created New Key"
    else:
        return "Issue Creating New key"
    
from bson import ObjectId

def getApiKeys(user_id: str):
    # Find the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Connect to org-specific database and api collection
    configdb = client[user_org["org"]]
    apiTable = configdb["api"]

    # Query all API keys in the org
    keys_cursor = apiTable.find({})

    # Convert keys to list of dicts, convert _id ObjectId to string 'id'
    keys = []
    for key_doc in keys_cursor:
        key_doc["id"] = str(key_doc.pop("_id"))
        keys.append(key_doc)

    return keys

def check_org(org: str) -> bool:
    existing_dbs = client.list_database_names()
    if org in existing_dbs:
        return True
      
    return False


def check_orgapi_map(org: str, api_key: str) -> bool:
    if org in client.list_database_names():
        configdb = client[org]
        api_table = configdb["api"]
        result = api_table.find_one({"key": api_key.replace("Bearer ","")})
        if result:
            return True
    return False

def get_email_api(api_key: str):
    token = api_key.replace("Bearer ", "")
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

    # Optional: check expiry field manually if not using `exp` claim
    email = payload.get("email")
    return email

