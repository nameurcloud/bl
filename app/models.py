from pydantic import BaseModel, EmailStr
from typing import List, Dict

class UserIn(BaseModel):
    email: EmailStr
    password: str
    fname: str
    lname: str
    mobile: str
    dob: str
    plan: str
    org: str

class UserLogIn(BaseModel):
    email: EmailStr
    password: str
    
class UserOut(BaseModel):
    id: str
    email: EmailStr

class RegionConfig(BaseModel):
    name: str
    code: str

class ResourceConfig(BaseModel):
    name: str
    code: str

class EnvironmentConfig(BaseModel):
    name: str
    code: str

class CloudConfig(BaseModel):
    regions: List[RegionConfig]
    resources: List[ResourceConfig]
    environments: List[EnvironmentConfig]

class ConfigBody(BaseModel):
    AWS: CloudConfig
    GCP: CloudConfig
    Azure: CloudConfig