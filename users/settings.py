import os, pathlib, gspread
from oauth2client.service_account import ServiceAccountCredentials

# secret, algorithm and token expiry time

SECRET_KEY = os.urandom(24).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080
TOKEN_URL = "/api/auth/token"

# google login
CLIENT_ID = "973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com"
base_path = pathlib.Path(__file__).parent.absolute()
CLIENT_SECRETS_JSON = str(base_path)+"/client_secret_973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com.json"
GSHEET_CLIENT = str(base_path)+"/gsheet-cred.json"

# gsheet
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://spreadsheets.google.com/feeds",	
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = 'test'
CREDS = ServiceAccountCredentials.from_json_keyfile_name(GSHEET_CLIENT, SCOPE)	
CLIENT = gspread.authorize(CREDS)