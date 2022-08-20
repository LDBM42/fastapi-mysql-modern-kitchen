from typing import Optional
from pydantic import BaseModel

class Step(BaseModel):
    id: Optional[int]
    number: int
    step: str

