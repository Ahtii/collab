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


def get_all_users(db: Session):
    response = {"users": ""}
    users = db.query(models.User).all()
    users_list = []
    for user in users:
        users_list.append(user.username)
    response["users"] = users_list
    return response


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
    return_response = {}
    # for protecting from CSRF
    if not request.headers.get("X-Requested-With"):
        return_response = {"error": "Something went wrong."}
    else:
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
                    db_user = register(db, user)
                    if "error" in db_user:
                        return_response = db_user
                access_token = gen_token(user.username)
                response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
            except:
                return_response = {"error": "Cannot authenticate"}
    return return_response


class SocketManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, models.User)] = []

    async def connect(self, websocket: WebSocket, user: models.User):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: models.User):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection[0].send_json(data)

    async def specific(self, data: dict):
        found_sender = False
        found_receiver = False
        for connection in self.active_connections:
            if found_sender and found_receiver:
                break
            if connection[1].username == data['sender']:
                await connection[0].send_json(data)
                found_sender = True
            elif connection[1].username == data['receiver']:
                await connection[0].send_json(data)
                found_receiver = True

    async def delete(self, user: models.User):
        for connection in self.active_connections:
            if connection[1].username == user.username:
                self.disconnect(connection[0], connection[1])
                print("from websockets")
                await self.get_online_users()
                break

    async def get_online_users(self):
        response = {"receivers": []}
        for connection in self.active_connections:
            print(connection[1].username)
            response['receivers'].append(connection[1].username)

        for connection in self.active_connections:
            response.update({"sender": connection[1].username})
            await connection[0].send_json(response)

    async def to_room_participants(self, data: dict):
        for connection in self.active_connections:
            print("checking for participants")
            print(connection[1].username)
            if connection[1].username in data['participants']:
                print("found match")
                print(connection[1].username)
                print("data to send is")
                print(data)
                await connection[0].send_json(data)


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


# create room
def create_room(user: models.User, room_data: validators.CreateRoom, db: Session):
    room = models.Room(
            name=room_data.name,
            admin=user.username,
            description=room_data.description
    )
    room.participants.append(user)
    for participant in room_data.participants:
        participant = participant.strip()
        user = db.query(models.User).filter(models.User.username == participant).first()
        if user:
            room.participants.append(user)
    db.add(room)
    db.commit()
    response = {"room": room.name}
    return response


# get rooms
def get_rooms(user: models.User, db: Session):
    rooms = db.query(models.Room).all()
    room_list = []
    for room in rooms:
        if user in room.participants:
            data = {
                "name": room.name,
                "description": room.description,
                "participants": room.participants
            }
            room_list.append(data)
    response = {"rooms": room_list}
    return response

# get room participants
def get_participants(room: str, db: Session):
    room = db.query(models.Room).filter(models.Room.name == room).first()
    if room:
        return [participant.username for participant in room.participants]
    return None
