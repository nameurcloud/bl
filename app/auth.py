from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException
from datetime import datetime, timedelta
from config import JWT_SECRET  # Make sure this is defined in config.py

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 Hash password
def hash_password(password: str):
    return pwd_context.hash(password)

# ✅ Verify password
def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

# 🔑 Create JWT token
def create_token(user_id: str):
    payload = {
        "sub": user_id,  # Standard claim for user ID
        "exp": datetime.utcnow() + timedelta(hours=5)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# 🔍 Decode and verify token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Optional: manual expiration check (can be skipped if `decode()` handles it)
        if payload.get("exp") and datetime.utcnow().timestamp() > payload["exp"]:
            raise HTTPException(status_code=400, detail="Token expired")

        user_id = payload.get("sub")  # ✅ Use 'sub' as the user_id
        if not user_id:
            raise HTTPException(status_code=403, detail="Invalid token payload")

        return user_id

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
