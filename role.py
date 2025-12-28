from pydantic import BaseModel

from typing import Annotated,Literal
from enum import Enum 

class Role_Schema(str,Enum):
    User="user"
    Admin="admin"
    Author="author"


Permission_ROLE = {
Role_Schema.User: {"view"},
Role_Schema.Admin: {"view", "edit","write"},
Role_Schema.Author: {"view", "edit","write"}  # ✅ fixed
}



Action=Literal["view","edit","write","delete","role_assign","me"]