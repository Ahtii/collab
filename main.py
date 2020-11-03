from sqlalchemy.orm import Session
import database
from users import validators, views, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

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

# for rendering social login front-end page
@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("social_login.html", {"request": request})

# register user
@app.post("/api/register/")
async def register(user: validators.RegisterValidator, db: Session = Depends(get_db)):
    print("inside register endpoint")
    return await views.register(db, user)

# login and generate token for further authentication
@app.post("/api/token")
async def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = views.authenticate(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = views.gen_token(user.username)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return

# logout the user by deleting the cookie
@app.post("/api/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"response": "logged out"}

# authenticating socail login and generating token
@app.post("/api/sociallogin", include_in_schema=False)
def social_login(request: Request, response: Response, data: validators.SocialLoginValidator, db: Session = Depends(get_db)):
    return views.social_login(db, request, response, data)

def get_user(db: Session = Depends(get_db), token: str = Depends(TOKEN_MANAGER)):
    return views.get_current_user(db, token)

@app.get("/api/greeting")
async def greeting(user: models.User = Depends(get_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized User")
    return {"response": "Welcome back "+user.username+"!"}


