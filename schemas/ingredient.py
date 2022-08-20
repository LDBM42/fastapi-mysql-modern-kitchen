from pydantic import BaseModel

class Ingredient(BaseModel):
    id: int
    ingredient: str