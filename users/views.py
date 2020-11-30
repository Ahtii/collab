from sqlalchemy.orm import Session
from users import models, validators
from passlib.context import CryptContext
from datetime import datetime, timedelta
from users import settings
from jose import jwt
from fastapi import HTTPException, status, Request, Response
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from typing import Optional
from fastapi import WebSocket
from typing import List
from oauth2client import client
import os, pathlib, random

# hashing password algorithm (BCRYPT for new hash) with support for old algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# generate hashed password
def gen_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_update_public_room(db: Session, user: models.User):
    room = db.query(models.Room).filter(models.Room.is_default == True).first()
    if room:
        room.participants.append(user)
    else:
        room = models.Room(
            name="Collab",
            admin="",
            description="This is a public room"
        )
    db.add(room)
    db.commit()

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
        #create_update_public_room(db, db_user)
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

# def gen_file_url(user, filename):
#     return os.path.join("/media/"+user+"/"+filename)

class SocketManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, models.User)] = []

    async def connect(self, websocket: WebSocket, user: models.User):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: models.User):
        self.active_connections.remove((websocket, user))

    async def broadcast(self,db: Session, data: dict):
        for connection in self.active_connections:
            await connection[0].send_json(data)

    async def to_specific_user(self, data: dict):
        found_sender = False
        found_receiver = False
        for connection in self.active_connections:
            if found_sender and found_receiver:
                break
            if connection[1].username == data['author']:
                print("data to be send to "+data['author'])
                print(data)
                await connection[0].send_json(data)
                found_sender = True
            elif connection[1].username == data['receiver']:
                print("data to be send to "+data['receiver'])
                print(data)
                await connection[0].send_json(data)
                found_receiver = True

    async def delete(self, user: models.User):
        for connection in self.active_connections:
            if connection[1].username == user.username:
                self.disconnect(connection[0], connection[1])
                await self.get_online_users()
                break

    async def get_online_users(self):
        response = {"receivers": []}
        for connection in self.active_connections:
            response['receivers'].append(connection[1].username)
        for connection in self.active_connections:
            response.update({"sender": connection[1].username})
            await connection[0].send_json(response)

    async def to_room_participants(self, data: dict):
        for connection in self.active_connections:
            if connection[1].username in data['participants']:
                await connection[0].send_json(data)

    async def populate_old_messages(self, data: dict):
        for connection in self.active_connections:
            if connection[1].username == data['user']:
                data.pop('user')
                print("data to be send")
                print(data)
                await connection[0].send_json(data)
                break

    async def recent_messages(self, data: dict):
        for connection in self.active_connections:
            if connection[1].username == data['cur_user']:
                await connection[0].send_json(data)
                break

    async def populate_rooms(self, rooms: list, user: models.User):
        for room in rooms:
            if user in room['participants']:
                for connection in self.active_connections:
                    if connection[1].username == user.username:
                        await connection[0].send_json(room)
                        break



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
        participants = room.participants
        if user in participants:
            data = {
                "name": room.name,
                "description": room.description,
                "participants": [participant.username for participant in participants]
            }
            room_list.append(data)
    response = {"rooms": room_list}
    return response

# generate file url
def gen_file_dir(directory, file):
    root = pathlib.Path(file).parent.absolute()
    relative_path = "/static/media/uploads"
    absolute_path = str(root) + relative_path
    target_url = os.path.join(absolute_path, directory)    
    return target_url

def create_file(dir, name, file):
    path = dir + "/" + name
    if os.path.isdir(dir):
        if os.path.isfile(path):
            bits = str(random.getrandbits(80))
            name_extension = path.split(".")
            path = name_extension[0] + bits + "." + name_extension[1]            
    else:
        os.mkdir(dir)
    with open(path, "wb") as f:
        f.write(file)
    return path

# get room participants
def get_participants(room: str, db: Session):
    room = db.query(models.Room).filter(models.Room.name == room).first()
    if room:
        return [participant.username for participant in room.participants]
    return None

# create message object and save it in db
def create_message(db: Session, data: dict):
    response = None
    try:
        sender_id = data['sender_id']
        username = data['username']
        if sender_id:
            message = models.PersonalMessage()
            message.text = data['message']
            message.sender_id = sender_id
            receiver = data['receiver']
            receiver = db.query(models.User).filter(
                models.User.username == receiver
            ).first()
            message.receiver_id = receiver.id
            print("message in:")
            print(message)
            file = data.get('file')
            print("our file is:")
            print(file)
            if file:
                message.attachment_url = file
            print("attempt save message")
            db.add(message)
            db.commit()
            print("saved message")
            response = {
                "author": username,
                "message": message.text,
                "date": message.created_date.strftime("%H:%M %p"),
                "receiver": receiver.username
            }
            if file:
                response.update({
                    "file": message.attachment_url,
                    "filename": data.get("filename")
                })
            print("response message: ")
            print(response)
        else:
            pass
    except:
        pass
    return response

def create_room_message(db: Session, data: dict):
    response = None
    try:
        room = db.query(models.Room).filter(
            models.Room.name == data['room']
        ).first()
        if room:
            sender = db.query(models.User).filter(
               models.User.username == data['user']
            ).first()
            if sender:
                message = models.RoomMessage()
                message.text = data['message']
                message.sender_id = sender.id
                message.room_id = room.id
                file = data.get('file')
                print("our file in room is")
                print(file)
                if file:
                    message.attachment_url = file
                db.add(message)
                db.commit()
                response = {
                    "author": sender.username,
                    "message": message.text,
                    "date": message.created_date.strftime("%H:%M %p"),
                    "room": room.name,
                    "participants": [participant.username for participant in room.participants]
                }
                if file:
                    response.update({
                        "file": message.attachment_url,
                        "filename": data.get("filename")
                    })
            else:
                pass
    except:
        pass
    return response