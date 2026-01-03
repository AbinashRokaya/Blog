from pydantic import BaseModel,EmailStr,field_validator,ValidationError
import re
from enum import Enum
from typing import List

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
    title:str
    category:str

# class category_schema(str,Enum):
class LikeRequest(BaseModel):
    post_id:int=None
 
class CommentRequest(BaseModel):
    post_id:int=None
    content:str=None

class Comment_Schema(BaseModel):
    comment:str
    user_name:str
class CommentResponse(BaseModel):
    comment_list:List[Comment_Schema]