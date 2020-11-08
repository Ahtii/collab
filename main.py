from sqlalchemy.orm import Session
import database
from users import validators, views, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import WebSocketDisconnect
from typing import Optional

app = FastAPI()
# authentication
TOKEN_MANAGER = OAuth2PasswordBearerWithCookie(tokenUrl="/api/token")
# websockets
socket_manager = views.SocketManager()

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

                                # API ENDPOINTS

@app.get("/api/current_user")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    return views.gen_response(user)

@app.get("/api/online_users")
def get_online_users():
    return socket_manager.get_online_users()

# create user
@app.post("/api/register")
async def create_user(user: validators.RegisterValidator, db: Session = Depends(get_db)):
    return views.register(db, user)

# login and generate token for further authentication
@app.post("/api/token")
async def authenticate(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = views.authenticate(db, credentials.username, credentials.password)
    response = {"error": "Incorrect username or password"}
    if user:
        response = Response()
        access_token = views.gen_token(user.username)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

# logout the user by deleting the cookie
@app.post("/api/logout")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        socket_manager.delete(user)
        response.delete_cookie("access_token")
    return user

# authenticating socail login and generating token
@app.post("/api/sociallogin", include_in_schema=False)
def social_login(request: Request, response: Response, data: validators.SocialLoginValidator, db: Session = Depends(get_db)):
    return views.social_login(db, request, response, data)

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: views.WebSocket, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    print("inside websockets")
    if user:
        await socket_manager.connect(websocket, user)
        print("got connected to "+user.username)
        try:
            print("inside try block")
            while True:
                data = await websocket.receive_json()
                reciever = data["client"]
                msg = data["message"]
                print(reciever)
                if reciever:
                    await socket_manager.specific(user.username, reciever, msg)
                else:
                    await socket_manager.broadcast(user.username, msg)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)
            # await manager.broadcast(f"{user.username} left")





