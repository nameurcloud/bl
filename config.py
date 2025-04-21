# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "your-default-secret")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

