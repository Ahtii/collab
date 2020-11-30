from sqlalchemy.orm import Session
import database, os, pathlib
from users import validators, views, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, Response, Request, Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from typing import List
from starlette.responses import FileResponse
from fastapi.responses import StreamingResponse
import random, magic

app = FastAPI()
# authentication
TOKEN_MANAGER = OAuth2PasswordBearerWithCookie(tokenUrl="/api/users/token")
# websockets
socket_manager = views.SocketManager()
# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

FILE_SIZE = 5000000

# create request session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")


# TEMPLATES

# home template
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# register template
@app.get("/register", include_in_schema=False)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# login template
@app.get("/login", include_in_schema=False)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# render file template
@app.get("/preview-file/", include_in_schema=False)
def preview_file(request: Request):    
    user = str(request.query_params['user'])
    filename = str(request.query_params['file'])  
    absolute_path = views.gen_file_dir(user, __file__) + "/" + filename    
    mime = magic.Magic(mime=True)
    mtype = mime.from_file(absolute_path)
    if "image" in mtype or "pdf" in mtype:
        return FileResponse(absolute_path, media_type=mtype)    
    else:
        return FileResponse(absolute_path, filename=filename)            
    # file = open(absolute_path, mode="rb")
    # return StreamingResponse(file, media_type=mtype)


# direct chat template
@app.get("/direct", include_in_schema=False)
def login(request: Request):
    return templates.TemplateResponse("direct.html", {"request": request})

# room chat template
@app.get("/rooms", include_in_schema=False)
def login(request: Request):
    return templates.TemplateResponse("rooms.html", {"request": request})

# room template
@app.get("/room", include_in_schema=False)
def login(request: Request):
    return templates.TemplateResponse("room.html", {"request": request})

    # API ENDPOINTS


@app.get("/api/user")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    response = {}
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        response = {"user": user.username}
    return response


# get all users
@app.get("/api/users")
def get_all_users(db: Session = Depends(get_db)):
    return views.get_all_users(db)


# create a user
@app.post("/api/users")
async def create_user(user: validators.RegisterValidator, db: Session = Depends(get_db)):
    return views.register(db, user)


# login the user and generate token for further authentication
@app.post("/api/users/token")
async def authenticate(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = views.authenticate(db, credentials.username, credentials.password)
    response = {"error": "Incorrect username or password"}
    if user:
        response = Response()
        access_token = views.gen_token(user.username)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


# logout the user
@app.delete("/api/users")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        await socket_manager.delete(user)
        response.delete_cookie("access_token")
    return user


# authenticating socail login and generating token
@app.post("/api/social_login", include_in_schema=False)
def social_login(request: Request, response: Response, data: validators.SocialLoginValidator,
                 db: Session = Depends(get_db)):
    return views.social_login(db, request, response, data)


def get_old_conversation(id):
    return "WITH cte AS (\
              SELECT *, ROW_NUMBER() OVER (PARTITION BY LEAST(sender_id, receiver_id),\
                                GREATEST(sender_id, receiver_id)\
                                ORDER BY created_date DESC) rn\
              FROM personal_message\
              WHERE sender_id = "+id+" OR receiver_id = "+id+"\
        )\
        SELECT sender_id, text, created_date, receiver_id, attachment_url\
        FROM cte\
        WHERE rn = 1;"


@app.websocket("/api/user-connect")
async def connect_user(websocket: views.WebSocket, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:
        await socket_manager.connect(websocket, user)
        await socket_manager.get_online_users()
        messages = db.execute(get_old_conversation(str(user.id)))
        for message in messages:
            sender = db.query(models.User).filter(
                models.User.id == message.sender_id
            ).first()
            receiver = db.query(models.User).filter(
                models.User.id == message.receiver_id
            ).first()
            msg_data = {
                "author": sender.username,
                "message": message.text,
                "date": message.created_date.strftime("%H:%M %p"),
                "receiver": receiver.username,
                "user": user.username
            }
            if message.attachment_url:
                filename = message.attachment_url.split("/")[-1]
                msg_data.update({
                    "file": str(message.attachment_url),
                    "filename": filename
                })
            await socket_manager.populate_old_messages(msg_data)
        response = views.get_rooms(user, db)
        rooms = response["rooms"]
        if rooms:
            await socket_manager.populate_rooms(rooms, user)
        try:
            while True:
                await websocket.receive_json()
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)


@app.websocket("/api/user-chat/{receiver}")
async def direct_chat(websocket: views.WebSocket, receiver: str, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:
        await socket_manager.connect(websocket, user)
        response = {"user": user.username}
        print("receiver")
        print(receiver)
        receiver = db.query(models.User).filter(models.User.username == receiver).first()
        old_messages = db.query(models.PersonalMessage).filter(
            ((models.PersonalMessage.sender_id == user.id) &
             (models.PersonalMessage.receiver_id == receiver.id)) |
            ((models.PersonalMessage.sender_id == receiver.id) &
             (models.PersonalMessage.receiver_id == user.id))
        ).order_by(models.PersonalMessage.created_date).all()
        for message in old_messages:
            if message.sender_id == user.id:
                sender_name = user.username
                receiver_name = receiver.username
            else:
                sender_name = receiver.username
                receiver_name = user.username
            msg_data = {
                "author": sender_name,
                "message": message.text,
                "date": message.created_date.strftime("%H:%M %p"),
                "receiver": receiver_name,
                "user": user.username
            }
            if message.attachment_url:
                filename = message.attachment_url.split("/")[-1]
                msg_data.update({
                    "file": str(message.attachment_url),
                    "filename": filename
                })
            # await socket_manager.specific(data)
            await socket_manager.populate_old_messages(msg_data)
        try:
            print("file is")
            print("testing")
            while True:
                data = await websocket.receive_json()
                receiver = data["receiver"]
                response.update(data)
                data = response
                data.update({"sender_id": user.id, "username": user.username})
                file_data = data.get('file')
                print("file here")
                print(file_data)
                if file_data:
                    file_size = file_data['size']
                    print("receiver is")
                    print(receiver)
                    if file_size <= FILE_SIZE:
                        file = await websocket.receive_bytes()
                        print("file is")
                        print(file)
                        print("data is")
                        print(data)
                        filename = file_data['filename']
                        file_dir = views.gen_file_dir(user.username, __file__)
                        file_url = views.create_file(file_dir, filename, file)
                        data.update({
                            "file": file_url,
                            "filename": filename
                        })
                        print(data)
                    else:
                        print("file size exceeded!")
                message = views.create_message(db, data)
                await socket_manager.to_specific_user(message)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)
            print("error occurred")
            # await manager.broadcast(f"{user.username} left")@app.websocket("/api/user-chat/{receiver}")

@app.websocket("/api/room-chat/{room}")
async def room_chat(websocket: views.WebSocket, room: str, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:
        await socket_manager.connect(websocket, user)
        room = db.query(models.Room).filter(models.Room.name == room).first()
        RoomMessage = models.RoomMessage
        old_messages = db.query(RoomMessage).filter(
            RoomMessage.room_id == room.id
        ).order_by(RoomMessage.created_date).all()
        for message in old_messages:
            if message.sender_id == user.id:
                sender_name = user.username
            else:
                sender = db.query(models.User).filter(
                    models.User.id == message.sender_id
                ).first()
                sender_name = sender.username
            msg_data = {
                "author": sender_name,
                "message": message.text,
                "date": message.created_date.strftime("%H:%M %p"),
                "room": room.name,
                "user": user.username
            }
            if message.attachment_url:
                filename = message.attachment_url.split("/")[-1]
                msg_data.update({
                    "file": str(message.attachment_url),
                    "filename": filename
                })
            await socket_manager.populate_old_messages(msg_data)
        try:
            while True:
                data = await websocket.receive_json()
                file_data = data.get('file')
                if file_data:
                    file_size = file_data['size']
                    if file_size <= FILE_SIZE:
                        file = await websocket.receive_bytes()
                        filename = file_data['filename']
                        file_dir = views.gen_file_dir(room.name, __file__)
                        file_url = views.create_file(file_dir, filename, file)
                        data.update({
                            "file": file_url,
                            "filename": filename
                        })
                message = views.create_room_message(db, data)
                await socket_manager.to_room_participants(message)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)
            # await manager.broadcast(f"{user.username} left")

            # ROOM ENDPOINTS


@app.post("/api/users/rooms")
async def create_room(request: Request, room_data: validators.CreateRoom, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        response = views.create_room(user, room_data, db)
        room = response['room']
        if room:
            response['participants'] = views.get_participants(room, db)
    else:
        response = {"error": "Unauthorized user"}
    return response


@app.get("/api/users/rooms")
def get_rooms(request: Request, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        response = views.get_rooms(user, db)
    else:
        response = {"error": "Unauthorized user"}
    return response

