from pydantic import BaseModel, ValidationError, validator
import html

# register validation
'''class RegisterValidator(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    is_social_account: bool = False'''

class RegisterValidator(BaseModel):
    full_name: str
    email: str
    password: str
    is_social_account: bool = False    

    # @validator('full_name')
    # def validate_fullname(cls, v):
    #     response = {}        
    #     if len(v) < 3:
    #         response['error'] = 'must not be less than 3 alphabets.'            
    #     elif len(v) > 30:
    #         response['error'] = 'must not be greater than 30 alphabets.'            
    #     else:
    #         response["value"] = v.lower()    
    #     return response

    # @validator('email')
    # def validate_email(cls, v):
    #     response = {}        
    #     if len(v) < 3:
    #         response['error'] = 'must not be less than 3 alphabets.'            
    #     elif len(v) > 30:
    #         response['error'] = 'must not be greater than 30 alphabets.'            
    #     else:
    #         response["value"] = v.lower()    
    #     return response   


# login validator
class LoginValidator(BaseModel):
    username: str
    password: str

# social login data
class SocialLoginValidator(BaseModel):
    type: str
    token: str

# social login data
class MessageValidator(BaseModel):
    message: str = None
    receiver: str = None   

# create room validator
class CreateRoom(BaseModel):
    name: str
    description: str = None
    participants: list

# create sheet validator
class CreateSheet(BaseModel):
    name: str
    participants: list    

# create room validator
class ProfileUpdateForm(BaseModel):
    fullname: str = None
    designation: str = None
    bio: str = None
    avatar: str = None    

