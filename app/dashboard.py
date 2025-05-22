from app.db import client, users
from bson import ObjectId


def getNameCount(user_id: str):
    # Get the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Use the user's org-specific database
    configdb = client[user_org["org"]]
    nameTable = configdb["names"]

    count = nameTable.count_documents({})
    return count

def getModeCount(user_id: str):
    # Get the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Use the user's org-specific database
    configdb = client[user_org["org"]]
    nameTable = configdb["names"]

    countUI = nameTable.count_documents({"mode" : "UI"})
    countAPI = nameTable.count_documents({"mode" : "API"})
    return_dict = {
        "UI" : countUI,
        "API" : countAPI
    }
    return return_dict

def getCSPCount(user_id: str):
    # Get the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Use the user's org-specific database
    configdb = client[user_org["org"]]
    patternTable = configdb["pattern"]

    # Get the single config document
    pattern = patternTable.find_one()
    if not pattern:
        return 0

    # Count all keys except _id
    csp_count = len([key for key in pattern.keys() if key != "_id"])

    return csp_count

def getCSPResRegCount(user_id: str):
    # Get the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Connect to the correct org-specific DB
    configdb = client[user_org["org"]]
    nameTable = configdb["pattern"]

    # Get the single config document
    pattern = nameTable.find_one()

    if not pattern:
        return []

    result = []
    for csp_key, csp_data in pattern.items():
        if csp_key == "_id":
            continue  # Skip MongoDB's _id field

        regions = csp_data.get("regions", [])
        resources = csp_data.get("resources", [])

        result.append({
            "csp": csp_key,
            "region": len(regions),
            "resource": len(resources),
        })

    return result
    