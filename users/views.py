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
from datetime import datetime
from dateutil import tz
import pytz

# hashing password algorithm (BCRYPT for new hash) with support for old algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# generate hashed password
def gen_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_timezone(d, timezone):
    d_utc = d.replace(tzinfo=tz.tzutc())
    d_local = d_utc.astimezone(pytz.timezone(timezone)).strftime("%H:%M %p")
    return d_local

# register logic
def register(db: Session, user: validators.RegisterValidator):
    response = {"user": None}
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
        response['user'] = db_user
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

def get_fullname(user: models.User):
    lastname = user.last_name
    fullname = user.first_name
    if lastname:
        fullname = fullname + " " + lastname
    return fullname

def get_all_users(db: Session):
    response = {"users": []}
    users = db.query(models.User).all()    
    for user in users:
        user_info = {
            "username": user.username,
            "fullname": get_fullname(user)
        }
        response["users"].append(user_info)    
    print(users)    
    return response


def get_lastname(data, first_name):
    last_name = ""
    if "family_name" in data.keys():
        last_name = data["family_name"].lower()
    else:
        name = data["name"]
        if name.isspace():
            name = name.split(" ").lower()
            if name.length > 1:
                if name[-1] != first_name:
                    last_name = name[-1]
    return last_name

def gen_username(db, username):
    users = db.query(models.User).filter(models.User.username.contains(username)).all()    
    if users:
        count = len(users)
        username = username[:3] + str(count)        
    return username 


# social login
def social_login(db: Session, request: Request, response: Response, data: validators.SocialLoginValidator):
    return_response = {"user": None}
    # for protecting from CSRF
    if not request.headers.get("X-Requested-With"):
        return_response.update({"error": "Something went wrong."})
    else :
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
                
                print(token_data)
                print(user_data)
                                
                user = validators.RegisterValidator(**user_data)
                db_user = db.query(models.User).filter(models.User.email == user.email).first()

                if db_user:
                    print("ind")                    
                    if user.email != db_user.email:   
                        print("me: ")
                        print(user.email)
                        print(db_user.email)                                             
                        db_user = None                    
                    # pass

                if db_user is None:
                    user.username = gen_username(db, user.username)
                    db_user = register(db, user)                                       
                    if "error" in db_user: 
                        return_response.update({"error": db_user["error"]})
                    else:
                        db_user = db_user["user"]    

                access_token = gen_token(user.username)                
                response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)                                
                return_response["user"] = db_user
                print("user loged in with email: ")
                print(db_user.email)
            except Exception as e:
                print(e)
                return_response.update({"error": "Cannot authenticate"})                
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

    async def get_online_users(self):
        response = {
            "online_users": []
        }    
        try:    
            for connection in self.active_connections:
                users = {
                    "username": connection[1].username,
                    "fullname": get_fullname(connection[1])
                }
                response['online_users'].append(users)
                #response['fullname'].append(get_fullname(connection[1]))
            for connection in self.active_connections:
                response.update({"sender": connection[1].username})    
                #response.update({"names": get_fullname(connection[1])})
                await connection[0].send_json(response)
        except Exception as e:
            print(e)  

    async def get_registered_users(self, users: list):
        
        registered_users = {"registered_users": []}
        
        for user in users:
            user_ifo = {
                "username": user.username,
                "fullname": get_fullname(user)
            }
            registered_users["registered_users"].append(user_ifo)

        for connection in self.active_connections:
            await connection[0].send_json(registered_users)

    async def to_specific_user(self, data: dict):
        found_sender = False
        found_receiver = False
        for connection in self.active_connections:
            if found_sender and found_receiver:
                break
            if connection[1].username == data['author']['username']:                
                await connection[0].send_json(data)
                found_sender = True
            elif connection[1].username == data['receiver']['username']:                
                await connection[0].send_json(data)
                found_receiver = True

    async def delete(self, user: models.User):
        for connection in self.active_connections:
            if connection[1].username == user.username:                
                await connection[0].close()
                #self.disconnect(connection[0], connection[1])
                await self.get_online_users()
                break

    async def get_stranger(self, user: models.User):
        msg_data = {
            "stranger": {
                "username": user.username,
                "fullname": get_fullname(user)
            }
        }
        for connection in self.active_connections:
            await connection[0].send_json(msg_data)

    async def sent_completed(self, user: models.User):
        for connection in self.active_connections:
            if connection[1].username == user.username:
                await connection[0].send_json({"completed": True})       

    async def to_room_participants(self, data: dict):
        for connection in self.active_connections:
            if connection[1].username in data['participants']:
                await connection[0].send_json(data)

    async def populate_old_messages(self, data: dict):
        for connection in self.active_connections:
            if connection[1].username == data['user']:
                data.pop('user')
                # print("data to be send")
                # print(data)
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
                "id": room.id,
                "name": room.name,
                "description": room.description,
                "participants": [participant.username for participant in participants]
            }
            room_list.append(data)
    response = {"rooms": room_list}
    return response

# generate file url
def gen_file_dir(directory, file, msg_file = True):
    root = pathlib.Path(file).parent.absolute()
    media_path = "/static/media"
    absolute_media_path = str(root) + media_path
    uploads = os.path.join(absolute_media_path, "uploads")    
    if not os.path.isdir(uploads):
        os.mkdir(uploads)
    absolute_path = absolute_media_path + "/uploads"
    user_dir = os.path.join(absolute_path, directory)
    if not os.path.isdir(user_dir):
        os.mkdir(user_dir)
    if msg_file:
        target_url = os.path.join(user_dir, "files")
        if not os.path.isdir(target_url):
            os.mkdir(target_url)
    else:
        target_url = os.path.join(user_dir, "profile")
        if not os.path.isdir(target_url):
            os.mkdir(target_url)

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
        sender = data['user']
        if sender:
            message = models.PersonalMessage()
            message.text = data['message']
            message.sender_id = sender.id            
            receiver = db.query(models.User).filter(
                models.User.username == data['receiver']
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
                "author": {
                    "username": sender.username,
                    "fullname": get_fullname(sender)
                },
                "message": message.text,
                "ist_date": get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                "est_date": get_timezone(message.created_date, "US/Eastern")  + " EST",                
                "receiver": {
                    "username": receiver.username,
                    "fullname": get_fullname(receiver)
                }
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
                    "author": {
                        "username": sender.username,
                        "fullname": get_fullname(sender)
                    },
                    "message": message.text,
                    "ist_date": get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                    "est_date": get_timezone(message.created_date, "US/Eastern")  + " EST",  
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