from sqlalchemy.orm import Session
import database
from users import validators, views, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

app = FastAPI()
# authentication
TOKEN_MANAGER = OAuth2PasswordBearerWithCookie(tokenUrl="/api/users/token")
# websockets
socket_manager = views.SocketManager()
# static files
app.mount("/static", StaticFiles(directory="static"), name="static")


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
        SELECT sender_id, text, created_date, receiver_id\
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
            data = {
                "author": sender_name,
                "message": message.text,
                "date": message.created_date.strftime("%H:%M %p"),
                "receiver": receiver_name,
                "user": response['user']
            }
            # await socket_manager.specific(data)
            await socket_manager.populate_old_messages(data)
        try:
            while True:
                data = await websocket.receive_json()
                receiver = data["receiver"]
                if receiver:
                    response.update(data)
                    data = response
                    data.update({"sender_id": user.id, "username": user.username})
                    message = views.create_message(db, data)
                    await socket_manager.to_specific_user(message)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)
            # await manager.broadcast(f"{user.username} left")@app.websocket("/api/user-chat/{receiver}")

@app.websocket("/api/room-chat/{room}")
async def room_chat(websocket: views.WebSocket, room: str, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:
        await socket_manager.connect(websocket, user)
        response = {"user": user.username}
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
            data = {
                "author": sender_name,
                "message": message.text,
                "date": message.created_date.strftime("%H:%M %p"),
                "room": room.name,
                "user": response['user']
            }
            await socket_manager.populate_old_messages(data)
        try:
            while True:
                data = await websocket.receive_json()
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

