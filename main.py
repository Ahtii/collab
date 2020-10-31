from sqlalchemy.orm import Session
import database
from users import validators, views, settings, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
#from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
#app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
TOKEN_MANAGER = OAuth2PasswordBearerWithCookie(tokenUrl="/api/token")

# create request session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# register user
@app.post("/api/register/")
async def register(user: validators.RegisterValidator, db: Session = Depends(get_db)):
    return views.register(db, user)


# login and generate token
# @app.post(settings.TOKEN_URL)
# async def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = views.authenticate(db, credentials.username, credentials.password)
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     access_token = views.gen_token(user.username)
#     return {"access_token" : access_token, "token_type": "bearer"}
#
def get_user(db: Session = Depends(get_db), token: str = Depends(TOKEN_MANAGER)):
    return views.get_current_user(db, token)

@app.post("/api/token")
async def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = views.authenticate(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = views.gen_token(user.username)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return


@app.get("/api/greeting")
async def greeting(user: models.User = Depends(get_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized User")
    return {"response": "Welcome back "+user.username+"!"}


@app.post("/api/logout")
async def logout(response: Response, token: str = Depends(TOKEN_MANAGER)):
    response.delete_cookie("access_token")
    return {"response": "logged out"}


