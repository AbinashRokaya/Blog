import jwt
from jwt.exceptions import InvalidTokenError
from schema import Token
from datetime import timedelta,datetime,timezone

SECRET_KEY = "c5b565981ec34e5b1192662a9d43c63dee6eef672712269ee459d3dc6a473972"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1


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
