from pydantic import BaseModel

# register validation
class RegisterValidator(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    is_social_account: bool = False

# login validator
class LoginValidator(BaseModel):
    username: str
    password: str

# social login data
class SocialLoginValidator(BaseModel):
    type: str
    token: str

