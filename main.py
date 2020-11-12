from sqlalchemy.orm import Session
import database
from users import validators, views, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
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
    return templates.TemplateResponse("login.html", {"request": request})\

# room template
@app.get("/room", include_in_schema=False)
def login(request: Request):
    return templates.TemplateResponse("room.html", {"request": request})

                                # API ENDPOINTS

@app.get("/api/user")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    return views.gen_response(user)

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
def social_login(request: Request, response: Response, data: validators.SocialLoginValidator, db: Session = Depends(get_db)):
    return views.social_login(db, request, response, data)

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: views.WebSocket, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:
        await socket_manager.connect(websocket, user)
        response = {"sender": user.username}
        await socket_manager.get_online_users()
        try:
            while True:
                data = await websocket.receive_json()
                receiver = data["receiver"]
                room = data["room"]
                msg = data["message"]
                if receiver:
                    response.update(data)
                    await socket_manager.specific(response)
                elif room:
                    participants = views.get_participants(room, db)
                    response.update({"participants": participants, "message": msg})
                    await socket_manager.to_room_participants(response)
                else:
                    response.update({"message": msg})
                    await socket_manager.broadcast(response)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)
            # await manager.broadcast(f"{user.username} left")


            # ROOM ENDPOINTS

@app.post("/api/users/rooms")
async def create_room(request: Request, room_data: validators.CreateRoom, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        response = views.create_room(user, room_data, db)
        print("room is")
        print(response)
        room = response['room']
        if room:
            response['participants'] = views.get_participants(room, db)
            await socket_manager.to_room_participants(response)
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





