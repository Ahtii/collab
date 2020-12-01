import os, pathlib

# secret, algorithm and token expiry time

SECRET_KEY = os.urandom(24).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
TOKEN_URL = "/api/auth/token"

# google login
CLIENT_ID = "973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com"
base_path = pathlib.Path(__file__).parent.absolute()
CLIENT_SECRETS_JSON = str(base_path)+"/client_secret_973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com.json"


