from datetime import datetime
from app.db import client, users
from bson import ObjectId


def set_payment_order(user_id: str, order: dict):

    configdb = client["authdb"]
    usertable = configdb["users"]

    # Prepare payment update fields
    update_fields = {
        "paymentDate": datetime.now(),
        "paymentOrderID": order.get("id"),
        "paymentStatus": order.get("status"),  # should be "created"
        "paymentAmount": order.get("amount"),
        "paymentReceipt": order.get("receipt"),
        "order": order
    }

    # Update the user record
    result = usertable.update_one(
        {"_id": ObjectId(user_id)},  # Match by Mongo _id
        {"$set": update_fields}
    )

    return result if result.acknowledged else ""

def set_payment(user_id: str, payment: dict):


    configdb = client["authdb"]
    usertable = configdb["users"]
     

     
    if payment.get("amount") == 199900:
        plan = "Essentials"
    if payment.get("amount") == 299900:
        plan = "Premium"
    if payment.get("amount") == 499900:
        plan = "Essentials+"
    if payment.get("amount") == 699900:
        plan = "Premium+"

    # Prepare payment update fields
    update_fields = {
    "paymentDate": datetime.now(),
    "paymentStatus": payment.get("status"),  # e.g., "captured"
    "paymentSummary": "Paid" if payment.get("status") == "captured" else "Not Paid",
    "paymentID": payment.get("id"),
    "paymentMethod": payment.get("method"),
    "payment": payment,
    "plan" : plan
}

    # Update the user record
    result = usertable.update_one(
        {"_id": ObjectId(user_id)},  # Match by Mongo _id
        {"$set": update_fields}
    )

    

    return result if result.acknowledged else ""
