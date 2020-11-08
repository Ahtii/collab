from sqlalchemy.orm import Session
from users import models, validators
from passlib.context import CryptContext
from datetime import datetime, timedelta
from users import settings
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
from starlette.status import HTTP_403_FORBIDDEN
import httplib2
from oauth2client import client
import random

# hashing password algorithm (BCRYPT for new hash) with support for old algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# generate hashed password
def gen_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# register logic
def register(db: Session, user: validators.RegisterValidator):
    response = {}
    if db.query(models.User).filter(models.User.email == user.email).first():
        response.update({"error": "email already exists"})
    elif db.query(models.User).filter(models.User.username == user.username).first():
        response.update({"error": "username already exists"})
    else:
        user = user.dict()
        user['password'] = gen_hash(user['password'])
        db_user = models.User(**user)
        db.add(db_user)
        db.commit()
    return response


# authenticated user
def authenticate(db: Session, username: str, password: str):
    user = db.query(models.User).filter((models.User.username == username) | (models.User.email == username)).first()
    if user:
        if not verify_password(password, user.password):
            return None
    return user


# get list of users
def get_all_users(db: Session):
    return db.query(models.User).all()


# generate token
def gen_token(username, time: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    data = {'sub': username}
    expires_in = timedelta(minutes=time)
    expire = datetime.utcnow() + expires_in
    data.update({'exp': expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def gen_response(user: models.User):
    response = {}
    if user:
        response["user"] = user.username
    return response


def get_payload(token: str):
    payload = None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except:
        pass
    return payload


# get username of currently logged in user
def get_current_user(db, token):
    user = None
    if token:
        token = token.split(" ")[1]
        payload = get_payload(token)
        if payload:
            username: str = payload.get("sub")
            user = db.query(models.User).filter(models.User.username == username).first()
    return user


def get_lastname(data, first_name):
    last_name = ""
    if "family_name" in data.keys():
        last_name = data["family_name"]
    else:
        name = data["name"]
        if name.isspace():
            name = name.split(" ").lower()
            if name.length > 1:
                if name[-1] != first_name:
                    last_name = name[-1]
    return last_name


# social login
def social_login(db: Session, request: Request, response: Response, data: validators.SocialLoginValidator):
    # for protecting from CSRF
    if not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=400, detail="Incorrect headers")

    data = data.dict()
    type = data['type'].strip().lower()
    auth_code = data['token']
    if type == "google":
        try:
            credentials = client.credentials_from_clientsecrets_and_code(
                settings.CLIENT_SECRETS_JSON, ['profile'],
                auth_code
            )
            token_data = credentials.id_token
            first_name = token_data["given_name"].lower()
            last_name = get_lastname(token_data, first_name)
            username = first_name + last_name
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": token_data["email"],
                "username": username,
                "password": "",
                "is_social_account": True
            }
            user = validators.RegisterValidator(**user_data)
            db_user = db.query(models.User).filter(models.User.username == user.username).first()
            if db_user is None:
                user = register(db, user)
            access_token = gen_token(user.username)
            response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        except:
            raise HTTPException(status_code=400, detail="Cannot be authenticated")


class SocketManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, models.User)] = []

    async def connect(self, websocket: WebSocket, user: models.User):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: models.User):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, sender: str, message: str):
        for connection in self.active_connections:
            await connection[0].send_text(sender+":"+message)

    async def specific(self, sender: str, reciever: str, message: str):
        print("inside specific")
        found_sender = False
        found_reciever = False
        for connection in self.active_connections:
            if found_sender and found_reciever:
                break
            if connection[1].username == sender:
                await connection[0].send_text(sender + ":" + message)
                found_sender = True
            elif connection[1].username == reciever:
                await connection[0].send_text(sender+":"+message)
                found_reciever = True

    def delete(self, user: models.User):
        for connection in self.active_connections:
            if connection[1].username == user.username:
                self.disconnect(connection[0], connection[1])

    def get_online_users(self):
        users = {"users": []}
        for connection in self.active_connections:
            users["users"].append(connection[1].username)
        return users


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl: str, scheme_name: str = None, scopes: dict = None, auto_error: bool = True):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"www-Authenticate": "Bearer"},
                )
            else:
                return None
        return param
