# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "l5-3tKsfg3y_983!hasjsg@xzd")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_0XHm0CZsK9Odpf")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET", "Zn6ppQ1H92riBDlpBFVri0Pa")

