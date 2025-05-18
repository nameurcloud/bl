from app.db import client, users
from bson import ObjectId
from app.models import apiKey


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
