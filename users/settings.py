import os

# secret, algorithm and token expiry time

SECRET_KEY = os.urandom(24).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
TOKEN_URL = "/api/auth/token"

# google login
CLIENT_ID = "973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com"
CLIENT_SECRETS_JSON = "/home/scareleven/collab/users/client_secret_973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com.json"


