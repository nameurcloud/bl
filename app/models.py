from pydantic import BaseModel, EmailStr
from typing import List, Dict
from datetime import datetime
from uuid import UUID

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
    code: str
    regions: List[RegionConfig]
    resources: List[ResourceConfig]
    environments: List[EnvironmentConfig]

class ConfigBody(BaseModel):
    AWS: CloudConfig
    GCP: CloudConfig
    Azure: CloudConfig

class GeneratedName(BaseModel):
    name : str
    datetime : datetime
    user : str
    mode : str
    status : str

class apiKey(BaseModel):
    id : UUID
    partialKey : str
    key : str
    email : str
    expiry : datetime
    permissions : list[str]