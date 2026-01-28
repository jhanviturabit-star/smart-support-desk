from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class CreateUser(BaseModel):
    username : str
    email : EmailStr
    password : str
    role : Literal['AGENT', 'TEAM_LEAD', 'ADMIN']

class LoginUser(BaseModel):
    email : EmailStr
    password : str