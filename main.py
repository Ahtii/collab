from sqlalchemy.orm import Session
import database
from users import validators, views
from fastapi import FastAPI, Depends

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
def create_user(user: validators.UserCreate, db: Session = Depends(get_db)):
    return views.register(db, user)

# login user
@app.post("/api/login/")
def authenticate(user: validators.AuthUser, db: Session = Depends(get_db)):
    return views.login(db, user)

# ----- USER MODEL FIELDS -----

# email       - required
# username    - required
# password    - required
# first_name  - required
# last_name
# is_active    -  default=False
# created_date
# modified_date
# is_verified  -  default=False
