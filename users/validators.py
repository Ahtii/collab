from pydantic import BaseModel

# register validation
class RegisterValidator(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

# login validator
class LoginValidator(BaseModel):
    username: str
    password: str