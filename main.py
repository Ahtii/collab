from sqlalchemy.orm import Session
import database
from users import validators, views, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

app = FastAPI()
TOKEN_MANAGER = OAuth2PasswordBearerWithCookie(tokenUrl="/api/token")

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

def get_user(token: str = Depends(TOKEN_MANAGER),db: Session = Depends(get_db)):
    return views.get_current_user(db, token)

# register template
@app.get("/register", include_in_schema=False)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# login template
@app.get("/login", include_in_schema=False)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# websocket template
@app.get("/chat", include_in_schema=False)
def login(request: Request, user: models.User = Depends(get_user)):
    if user is None:
        return {"error": "Unauthorized user please login"}
    return templates.TemplateResponse("chat.html", {"request": request})

                                # API ENDPOINTS

@app.get("/api/current_user")
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    user = views.get_current_user(token)
    user = user.dict()
    return user

@app.post("/api/register")
async def create_user(user: validators.RegisterValidator, db: Session = Depends(get_db)):
    response = views.register(db, user)
    if response == {}:
        return RedirectResponse(url="/login", status_code=302)
    return response

# login and generate token for further authentication
@app.post("/api/token")
async def authenticate(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = views.authenticate(db, credentials.username, credentials.password)
    response = {"error": "Incorrect username or password"}
    if user:
        #response = Response()
        response = RedirectResponse(url="/chat", status_code=302)
        access_token = views.gen_token(user.username)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

# logout the user by deleting the cookie
@app.post("/api/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return RedirectResponse(url="/", status_code=302)

# authenticating socail login and generating token
@app.post("/api/sociallogin", include_in_schema=False)
def social_login(request: Request, response: Response, data: validators.SocialLoginValidator, db: Session = Depends(get_db)):
    return views.social_login(db, request, response, data)

# websockets simple example

from fastapi import WebSocket

from typing import List
from fastapi import WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, models.User)] = []

    async def connect(self, websocket: WebSocket, user: models.User):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: models.User):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection[0].send_text(message)

    async def specific(self, message: str, user: models.User):
        for connection in self.active_connections:
            if connection[1] == user:
                await connection[0].send_text(message)
                break

manager = ConnectionManager()

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    token = websocket.cookies.get("access_token")
    token = token.split(" ")[1]
    print(token)
    user = views.get_current_user(db, token)
    if user:
        await manager.connect(websocket, user)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast(f"{user.username} says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket, user)
            await manager.broadcast(f"{user.username} left")





