from fastapi.security import OAuth2PasswordBearer
from starlette.config import Config
import os

# secret, algorithm and token expiry time

SECRET_KEY = os.urandom(24).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
TOKEN_URL = "/api/auth/token"

# token manager
#TOKEN_MANAGER = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)

