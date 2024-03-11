from passlib.context import CryptContext


# Biramo koji cemo hashing algoritam da koristimo
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)
