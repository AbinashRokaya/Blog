import jwt
from jwt.exceptions import InvalidTokenError
from schema import Token
from datetime import timedelta,datetime,timezone
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


def create_access_token(subject: str,
    role: str,expires_delta: timedelta | None = None):
    to_encode = to_encode = {
        "sub": subject,    
        "role": role       
    }
    if expires_delta:
        expire=datetime.now(timezone.utc)+expires_delta
    else:
        expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp":expire})
    encode_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encode_jwt)
    return encode_jwt
