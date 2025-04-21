from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    email: EmailStr
    password: str
    fname: str
    lname: str
    mobile: str
    dob: str

class UserLogIn(BaseModel):
    email: EmailStr
    password: str
    
class UserOut(BaseModel):
    id: str
    email: EmailStr