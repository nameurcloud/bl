from datetime import datetime
from app.db import client, users
from bson import ObjectId
from app.models import GeneratedName


def set_name(user_id: str, name: GeneratedName):
    # Get the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})  
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Use the user's org-specific database
    configdb = client[user_org["org"]]
    nametable = configdb["names"]

    # Count existing names with the same prefix
    count_of_pattern = nametable.count_documents({
        "name": {"$regex": f"^{name.name}"}
    })

    # Append suffix to the name (optional logic depending on your naming pattern)
    updated_name = f"{name.name}{count_of_pattern + 1:05d}"

    # Set the new name and submitted status
    name_dict = name.dict()
    name_dict["name"] = updated_name
    name_dict["status"] = "submitted"

    # Insert the document
    insert_result = nametable.insert_one(name_dict)

    if insert_result.acknowledged :
        return updated_name
    else:
        return ""


def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def get_name(user_id: str):
    # Get the user's organization
    user_org = users.find_one({"_id": ObjectId(user_id)}, {"org": 1})
    if not user_org or "org" not in user_org:
        raise ValueError("Organization not found for user.")

    # Use the user's org-specific database
    configdb = client[user_org["org"]]
    nametable = configdb["names"]

    # Find all documents in the 'names' collection
    results = list(nametable.find())

    # Serialize ObjectId to string
    return [serialize_doc(doc) for doc in results]

def get_name_api(org: str):
    # Get the user's organization

    if not org :
        raise ValueError("Organization not found for user.")

    # Use the user's org-specific database
    configdb = client[org]
    nametable = configdb["names"]

    # Find all documents in the 'names' collection
    results = list(nametable.find({}, {"name": 1, "_id": 0}))

    # Serialize ObjectId to string
    return results


def set_name_api(org: str, pattern: str, email : str):
    if not org:
        raise ValueError("Organization not found for user.")

    configdb = client[org]
    nametable = configdb["names"]

    # Count matching existing names
    count_of_pattern = nametable.count_documents({
        "name": {"$regex": f"^{pattern}"}
    })

    patternexist = count_of_pattern  # This handles both pattern exist check and suffix count
    if patternexist == 0:
       return f"First name with the pattern: {pattern} needs to be created from UI"

    updated_name = f"{pattern}{count_of_pattern + 1:05d}"

    name_dict = {
        "name": updated_name,
        "datetime": datetime.now(),
        "user": email,
        "mode": "API",
        "status": "submitted"
    }

    insert_result = nametable.insert_one(name_dict)

    if insert_result.acknowledged:
        return updated_name
    else:
        return ""