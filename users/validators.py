from pydantic import BaseModel

# register validation
class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_active: bool
    created_date: str = None
    modified_date: str = None
    is_verified: bool

    class Config:
        orm_mode = True

# login validation
class AuthUser(BaseModel):
    username: str
    password: str

