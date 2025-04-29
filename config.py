# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "l5-3tKsfg3y_983!hasjsg@xzd")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

