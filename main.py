from sqlalchemy.orm import Session
import database
from users import validators, views, settings
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

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
@app.post(settings.TOKEN_URL)
async def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = views.authenticate(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = views.gen_token(user.username)
    return {"access_token" : access_token, "token_type": "bearer"}

def get_user(db: Session = Depends(get_db), token: str = Depends(settings.TOKEN_MANAGER)):
    return views.get_current_user(db, token)

@app.get("/api/greeting")
async def greeting(response: str = Depends(get_user)):
    return response

