from pydantic import BaseModel,EmailStr,field_validator,ValidationError
import re

class RegisterRequest(BaseModel):
    name:str=None
    address:str=None
    email:EmailStr=None
    password:str=None

    @field_validator('password')
    @classmethod
    def correct_password(cls,v): 
        if len(v) < 5:
            raise ValueError('Password must be at least 8 characters long.')
        if not any(char.isupper() for char in v):
            raise ValueError('Password should contain at least one uppercase character.')
        if not any(char.islower() for char in v):
            raise ValueError('Password should contain at least one lowercase character.')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password should contain at least one digit.')
        return v



class LoginRequest(BaseModel):
    username: str=None
    password: str=None

class Token(BaseModel):
    token:str
    token_type:str

class PostRequest(BaseModel):
    content:str