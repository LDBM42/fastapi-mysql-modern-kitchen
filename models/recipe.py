from sqlalchemy import CheckConstraint, Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from config.db import engine #, Meta


Base = declarative_base()

user_favorite_recipe = Table(
    "user_favorite_recipe",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String(255))
    password = Column(String(255))
    gender = Column(String(255))
    photo = Column(String(255))
    recipe_id = relationship('Recipe', backref=backref('users'))
    favorite_recipes = relationship(
        "Recipe", secondary=user_favorite_recipe, back_populates="users_favorite"
    )


class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    ingredients = relationship('Ingredient', backref=backref('recipes'))
    steps = relationship('Step')
    photo = Column(String(255))
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    users_favorite = relationship(
        "User", secondary=user_favorite_recipe, back_populates="favorite_recipes"
    )


class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    ingredient = Column(String(255))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))


class Step(Base):
    __tablename__ = 'steps'

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    step = Column(String(255))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))


Base.metadata.create_all(engine)
# meta.create_all(engine)