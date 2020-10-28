from sqlalchemy.orm import Session
from users import models, validators
from passlib.context import CryptContext
from datetime import datetime, timedelta
from users import settings
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

# hashing password algorithm (BCRYPT for new hash) with support for old algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# check for registered email
def already_registered(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# generate hashed password
def gen_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# register logic
def register(db: Session, user: validators.RegisterValidator):
    if already_registered(db, user.email):
        return {"Error", "Email already registered"}
    user = user.dict()
    user['password'] = gen_hash(user['password'])
    db_user = models.User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# authenticated user
def authenticate(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        if not verify_password(password, user.password):
            return None
    return user


# login logic
def login(db: Session, user: validators.LoginValidator):
    response = {"response": "username or password did not match!"}
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) &
        (models.User.password == user.password)
    ).first()
    if db_user:
        response["response"] = "Welcome back, " + user.username + "!"
    return response


# get list of users
def get_all_users(db: Session):
    return db.query(models.User).all()


# generate token
def gen_token(username):
    data = {'sub': username}
    expires_in = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_in
    data.update({'exp': expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# get username of currently logged in user
def get_current_user(db, token):
    response = {"Unauthorized": "Not valid credentials"}
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    username: str = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        response = {"Greeting": "Welcome back " + user.username + "!"}
    return response
