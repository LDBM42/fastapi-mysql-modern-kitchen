from pydantic import BaseModel

class Favorite(BaseModel):
    user_id: int
    recipe_id: int