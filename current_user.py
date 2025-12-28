from auth import oauth2_schema
from typing import Annotated
import jwt
from jwt_token import SECRET_KEY,ALGORITHM
from fastapi import HTTPException,Depends,Cookie
from role import Permission_ROLE
from role import Role_Schema,Action
def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None
):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")

        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        role_enum = Role_Schema(role.lower()) 

        return {
            "username": username,
            "role": role_enum
        }

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def require_permission(action:Action):
    def dependency(user=Depends(get_current_user)):
        role=user["role"]

        if action not in Permission_ROLE.get(Role_Schema(role),set()):
             raise HTTPException(
                status_code=403,
                detail=f"{role} is not allowed to perform '{action}'"
            )
        return user
    return dependency

