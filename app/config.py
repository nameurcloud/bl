from app.db import client, users
from bson import ObjectId

def get_user_pattern_config(user_id: str):
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    configdb = client[user_org["org"]]
    pattern_collection = configdb["pattern"]
    config = pattern_collection.find_one()

    if config and "_id" in config:
        del config["_id"]  # remove ObjectId if not needed in the response

    return config



def set_user_pattern_config(user_id: str, updated_config):
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    configdb = client[user_org["org"]]
    pattern_collection = configdb["pattern"]

    # Remove any previous config for this org
    pattern_collection.delete_many({})

    # Store the entire nested config object in one document
    insert_result = pattern_collection.insert_one(updated_config.dict())
    print(insert_result)

    return str(insert_result.inserted_id)