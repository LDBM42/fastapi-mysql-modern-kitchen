from typing import Optional
from pydantic import BaseModel

from enum import Enum

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class User(BaseModel):
    id: Optional[int]
    nickname: str
    password: str
    gender: Gender
    photo: str # File photo:

class UpdateUser(BaseModel):
    id: Optional[int]
    nickname: Optional[str]
    password: Optional[str]
    gender: Optional[str]
    photo:Optional[str] # File photo: