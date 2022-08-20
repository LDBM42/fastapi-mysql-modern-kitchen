from typing import List
from pydantic import BaseModel
from schemas.user import User
from datetime import datetime
from typing import Optional

class Recipe(BaseModel):
    id: Optional[int] 
    name: str
    description: str
    ingredients: Optional[List[str]] 
    steps: Optional[List[str]] 
    photo: str # File
    date: datetime
    user: User