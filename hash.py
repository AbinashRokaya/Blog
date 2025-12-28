from passlib.context import CryptContext

pwd=CryptContext(schemes=['bcrypt'], deprecated="auto")


def hash_password(password):
    return pwd.hash(password)

def verify_password(current_password,hased_password):
    return pwd.verify(current_password,hased_password)