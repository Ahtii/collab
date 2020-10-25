from sqlalchemy.orm import Session
from users import models, validators

# check for registered email
def already_registered(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# register logic
def register(db: Session, user: validators.UserCreate):
    if already_registered(db, user.email):
        return {"Error", "Email already registered"}
    user = user.dict()
    db_user = models.User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# login logic
def login(db: Session, user: validators.AuthUser):
    response = {"response": "username or password did not match!"}
    db_user = db.query(models.User).filter(
                        (models.User.username == user.username) &
                        (models.User.password == user.password)
                        ).first()
    if db_user:
        response["response"] = "Welcome back, "+user.username+"!"
    return response