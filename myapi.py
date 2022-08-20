from ast import And
import json
import os
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import and_, asc, desc
from config.db import conn, engine

from sqlalchemy.orm import sessionmaker

from cryptography.fernet import Fernet

from models.recipe import Recipe as recipes
from models.recipe import Ingredient as ingredients
from models.recipe import Step as steps
from models.recipe import User as users
from models.recipe import user_favorite_recipe

from schemas.recipe import Recipe 
from schemas.ingredient import Ingredient
from schemas.step import Step
from schemas.user import User, UpdateUser
from schemas.favorite import Favorite

app = FastAPI(
    title="Cook Book Modern Kitchen API",
    description="This is the API used in the mobile app CookBook Modern Kitchen",
    version='0.0.1',
)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

key = Fernet.generate_key()
f = Fernet(key)

# @app.post("/files")
# async def UploadImage(file: bytes = File(...)):
#     print(file)
#     with open('image.jpg','wb') as image:
#         image.write(file)
#         image.close()
#     return 'got it'





@app.post("/uploadfile")
async def UploadImage(file: UploadFile, src: str):
    with open(os.path.join(src, file.filename),'wb') as image:
        image.write(await file.read())
        image.close()
    
    # to refresh the session when creating new user
    session.refresh()
    
    return {"filename": file.filename}


@app.get("/img", response_class=FileResponse)
async def getImage(imgpath: str):
    return FileResponse(path=imgpath)



@app.get('/recipe-by-id')
def get_recipe(id: int):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        recipe_returned = dict(
            session.query(
                recipes.name, recipes.description, recipes.photo, recipes.date)
                .filter(recipes.id == id).first()
        )

        ingredients_returned = session.query(ingredients.ingredient).filter(ingredients.recipe_id == id).all()
        steps_returned = session.query(steps.number, steps.step).filter(steps.recipe_id == id).all()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()
    
    # convert to list
    ingredient_list = [dict(ingr)['ingredient'] for ingr in ingredients_returned]
    step_list = [dict(stp)['step'] for stp in steps_returned]

    # assign ingredients and steps to the ecipe
    recipe_returned['ingredients'] = ingredient_list
    recipe_returned['steps'] = step_list

    return recipe_returned

@app.get('/recipes')
def get_recipe():
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        recipes_returned = (
            session.query(
                recipes.name, recipes.description, recipes.date, 
                ingredients.ingredient, steps.step, 
                recipes.user_id, recipes.photo, steps.number, recipes.id)
                .join(ingredients, steps)
                .order_by(asc(recipes.id))
                .order_by(asc(steps.number))
                ).all()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()


    # GIVE FORMAT TO THE JSON -----------------------------------------------------------------------
    fr_index = 0
    formatted_recipes = [{"name": recipes_returned[0][0], "description": recipes_returned[0][1], "date": recipes_returned[0][2], "ingredient": [recipes_returned[0][3]], "step": [f"{str(recipes_returned[0][7])}___{recipes_returned[0][4]}"], "user_id": recipes_returned[0][5], "photo": recipes_returned[0][6], "id": recipes_returned[0][8]}]


    for i, recs in enumerate(recipes_returned):
        if i == 0: continue

        if (recs[0] == formatted_recipes[fr_index]["name"]):
            formatted_recipes[fr_index]["ingredient"].append(recs[3])
            formatted_recipes[fr_index]["step"].append(f"{str(recs[7])}___{recs[4]}")
        else:
            # conver to set and sort steps asc, to delete repeted elements
            formatted_recipes[fr_index]["ingredient"] = list(set(formatted_recipes[fr_index]["ingredient"]))
            formatted_recipes[fr_index]["step"] = sorted(set(formatted_recipes[fr_index]["step"]))
            # delete number from steps
            for i, step in enumerate(formatted_recipes[fr_index]["step"]):
                index_found = formatted_recipes[fr_index]["step"][i].find("___")
                # delete the pattern used to sort the steps ([number]___)
                formatted_recipes[fr_index]["step"][i] = formatted_recipes[fr_index]["step"][i][index_found+3:]

            fr_index+=1
            formatted_recipes.append({"name": recs[0], "description": recs[1], "date": recs[2], "ingredient": [recs[3]], "step": [f"{str(recs[7])}___{recs[4]}"], "user_id": recs[5], "photo": recs[6], "id": recs[8]})


    # conver last element (-1) to set and back to list, to delete repeted elements
    formatted_recipes[-1]["ingredient"] = list(set(formatted_recipes[-1]["ingredient"]))
    formatted_recipes[-1]["step"] = sorted(set(formatted_recipes[-1]["step"])) # delete number from steps
    for i, step in enumerate(formatted_recipes[-1]["step"]):
        index_found = int(formatted_recipes[-1]["step"][i].find("___"))
        # delete the pattern used to sort the steps ([number]___)
        formatted_recipes[-1]["step"][i] = formatted_recipes[-1]["step"][i][index_found+3:]
    # ----------------------------------------------------------------------------------------
    return formatted_recipes

@app.get('/recipes-by-user-id')
def get_recipe(userId: int):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        recipes_returned = (
            session.query(
                recipes.name, recipes.description, recipes.date, 
                ingredients.ingredient, steps.step, 
                recipes.user_id, recipes.photo, steps.number, recipes.id)
                .filter_by(user_id = userId)
                .join(ingredients, steps)
                .order_by(asc(recipes.id))
                .order_by(asc(steps.number))
                ).all()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()

    # GIVE FORMAT TO THE JSON -----------------------------------------------------------------------
    fr_index = 0
    formatted_recipes = [{"name": recipes_returned[0][0], "description": recipes_returned[0][1], "date": recipes_returned[0][2], "ingredient": [recipes_returned[0][3]], "step": [f"{str(recipes_returned[0][7])}___{recipes_returned[0][4]}"], "user_id": recipes_returned[0][5], "photo": recipes_returned[0][6], "id": recipes_returned[0][8]}]


    for i, recs in enumerate(recipes_returned):
        if i == 0: continue

        if (recs[0] == formatted_recipes[fr_index]["name"]):
            formatted_recipes[fr_index]["ingredient"].append(recs[3])
            formatted_recipes[fr_index]["step"].append(f"{str(recs[7])}___{recs[4]}")
        else:
            # conver to set and sort steps asc, to delete repeted elements
            formatted_recipes[fr_index]["ingredient"] = list(set(formatted_recipes[fr_index]["ingredient"]))
            formatted_recipes[fr_index]["step"] = sorted(set(formatted_recipes[fr_index]["step"]))
            # delete number from steps
            for i, step in enumerate(formatted_recipes[fr_index]["step"]):
                index_found = formatted_recipes[fr_index]["step"][i].find("___")
                # delete the pattern used to sort the steps ([number]___)
                formatted_recipes[fr_index]["step"][i] = formatted_recipes[fr_index]["step"][i][index_found+3:]

            fr_index+=1
            formatted_recipes.append({"name": recs[0], "description": recs[1], "date": recs[2], "ingredient": [recs[3]], "step": [f"{str(recs[7])}___{recs[4]}"], "user_id": recs[5], "photo": recs[6], "id": recs[8]})


    # conver last element (-1) to set and back to list, to delete repeted elements
    formatted_recipes[-1]["ingredient"] = list(set(formatted_recipes[-1]["ingredient"]))
    formatted_recipes[-1]["step"] = sorted(set(formatted_recipes[-1]["step"])) # delete number from steps
    for i, step in enumerate(formatted_recipes[-1]["step"]):
        index_found = int(formatted_recipes[-1]["step"][i].find("___"))
        # delete the pattern used to sort the steps ([number]___)
        formatted_recipes[-1]["step"][i] = formatted_recipes[-1]["step"][i][index_found+3:]
    # ----------------------------------------------------------------------------------------
    return formatted_recipes

@app.post('/recipes')
def create_recipe(recipe: Recipe):
    # get the table from the class
    recipe_table = recipes.metadata.tables['recipes']
    ingredient_table = ingredients.metadata.tables['ingredients']
    step_table = steps.metadata.tables['steps']
    user_table = users.metadata.tables['users']

    user = (
        session.query(users)
        .filter(users.nickname == recipe.user.nickname).first()
    )

    # here we create a dict to store the data in this format
    new_recipe = {'name': recipe.name, 
                'description': recipe.description,
                'photo': recipe.photo,
                'date': recipe.date,
                'user_id':  user.id
                }

    result = conn.execute(recipe_table.insert().values(new_recipe))

    recipe_id = result.lastrowid # get the recipe id
    # create a dic to create many registers in the steps and ingredients table
    ing = [{'ingredient': ingredient, 'recipe_id': recipe_id}  for ingredient in recipe.ingredients]
    ste = [{'step': step, 'number': number+1, 'recipe_id': recipe_id}  for number, step  in enumerate(recipe.steps)]
    
    # insert steps and ingredients
    conn.execute(ingredient_table.insert(), ing)
    conn.execute(step_table.insert(), ste)

    # # print(result.lastrowid) # this returns the last row ID
    # # new_recipe.c.id means the user in the column id
    # # this excecute a select where the id is iqual to the last id added to the database
    # # .first() is to return the first element of the list
    return conn.execute(recipe_table.select().where(recipe_table.c.id == recipe_id)).first()
    # return session.query(recipes).filter(recipes.id == recipe_id).first()
    
@app.put('/recipes')
def update_recipe(recipe: Recipe):
    # get the table from the class
    recipe_table = recipes.metadata.tables['recipes']
    ingredient_table = ingredients.metadata.tables['ingredients']
    step_table = steps.metadata.tables['steps']
    user_table = users.metadata.tables['users']

    user = (
        session.query(users)
        .filter(users.nickname == recipe.user.nickname).first()
    )

    # here we create a dict to store the data in this format
    updated_recipe = {'name': recipe.name, 
                'description': recipe.description,
                'photo': recipe.photo,
                'date': recipe.date,
                'user_id':  user.id
                }

    conn.execute(recipe_table.update().
    where(recipe_table.c.id == recipe.id).
    values(updated_recipe))

    # create a dic to create many registers in the steps and ingredients table
    ing = [{'ingredient': ingredient, 'recipe_id': recipe.id}  for ingredient in recipe.ingredients]
    ste = [{'step': step, 'number': number+1, 'recipe_id': recipe.id}  for number, step  in enumerate(recipe.steps)]
    
    conn.execute(ingredient_table.delete().where(ingredient_table.c.recipe_id == recipe.id))
    conn.execute(step_table.delete().where(step_table.c.recipe_id == recipe.id))

    # insert steps and ingredients
    conn.execute(ingredient_table.insert(), ing)
    conn.execute(step_table.insert(), ste)

    return True




@app.get('/user')
def get_user(nickname: str):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        return session.query(users).filter(users.nickname == nickname).first()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()
    

@app.get('/users')
def get_users():
    return session.query(users.id, users.nickname).all()


@app.post('/users')
def create_user(user: User):
    # this is to access the table from the class
    user_table = users.metadata.tables['users']

    # here we create a dict to store the data as a json
    new_user = {'nickname': user.nickname,
                'password': user.password,
                'gender': user.gender,
                'photo': user.photo}

    result = conn.execute(user_table.insert().values(new_user))
    #  return conn.execute(user_table.select().where(user_table.c.id == result.lastrowid)).first()
    return session.query(users).filter(users.id == result.lastrowid).first()

# put is to update
@app.put('/users', response_model=bool, tags=['users'])
def update_user(user: User):
    
    # this is to access the table from the class
    user_table = users.metadata.tables['users']

    # here we create a dict to store the data as a json
    updated_user = {'nickname': user.nickname,
                'password': user.password,
                'gender': user.gender,
                'photo': user.photo}


    # execute update
    conn.execute(user_table.update()
    .where(user_table.c.nickname == user.nickname)
    .values(updated_user))

    return True



@app.get('/favorites')
def get_favorites(user_id: int):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        result = session.query(user_favorite_recipe.c.recipe_id).filter(user_favorite_recipe.c.user_id == user_id).all()
        # convert result to list
        result = [recipe_id[0] for recipe_id in result]

        recipes_returned = (
            session.query(
                recipes.name, recipes.description, recipes.date, 
                ingredients.ingredient, steps.step, 
                recipes.user_id, recipes.photo, steps.number, recipes.id)
                # .filter_by(user_id = user_id)
                .filter(recipes.id.in_(result))
                .join(ingredients, steps)
                .order_by(asc(recipes.id))
                .order_by(asc(steps.number))
                ).all() 
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()

    
    # GIVE FORMAT TO THE JSON -----------------------------------------------------------------------
    fr_index = 0
    formatted_recipes = [(
            {
                "name": recipes_returned[0][0],
                "description": recipes_returned[0][1],
                "date": recipes_returned[0][2],
                "ingredient": [recipes_returned[0][3]],
                "step": [str(recipes_returned[0][7]) + "___" + recipes_returned[0][4]],
                "user_id": recipes_returned[0][5],
                "photo": recipes_returned[0][6],
                "id": recipes_returned[0][8],
            })]

    for i, recs in enumerate(recipes_returned):
        if i == 0: continue

        if (recs[0] == formatted_recipes[fr_index]["name"]):
            formatted_recipes[fr_index]["ingredient"].append(recs[3])
            formatted_recipes[fr_index]["step"].append(str(recs[7]) + "___" + recs[4])
        else:
            # conver to set and sort steps asc, to delete repeted elements
            formatted_recipes[fr_index]["ingredient"] = list(set(formatted_recipes[fr_index]["ingredient"]))
            formatted_recipes[fr_index]["step"] = sorted(set(formatted_recipes[fr_index]["step"]))
            # delete number from steps
            for i, step in enumerate(formatted_recipes[fr_index]["step"]):
                index_found = formatted_recipes[fr_index]["step"][i].find("___")
                # delete the pattern used to sort the steps ([number]___)
                formatted_recipes[fr_index]["step"][i] = formatted_recipes[fr_index]["step"][i][index_found+3:]

            fr_index+=1
            formatted_recipes.append(
            {
                "name": recs[0],
                "description": recs[1],
                "date": recs[2],
                "ingredient": [recs[3]],
                "step": [str(recs[7]) + "___" + recs[4]],
                "user_id": recs[5],
                "photo": recs[6],
                "id": recs[8],
            })

    # conver last element (-1) to set and back to list, to delete repeted elements
    formatted_recipes[-1]["ingredient"] = list(set(formatted_recipes[-1]["ingredient"]))
    formatted_recipes[-1]["step"] = sorted(set(formatted_recipes[-1]["step"])) # delete number from steps
    for i, step in enumerate(formatted_recipes[-1]["step"]):
        index_found = int(formatted_recipes[-1]["step"][i].find("___"))
        # delete the pattern used to sort the steps ([number]___)
        formatted_recipes[-1]["step"][i] = formatted_recipes[-1]["step"][i][index_found+3:]
    # ----------------------------------------------------------------------------------------
    return formatted_recipes


@app.get('/favorite')
def get_is_favorite(user_id: int, recipe_id: int):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        result = session.query(user_favorite_recipe.c.recipe_id).filter(user_favorite_recipe.c.user_id == user_id).all()
        # convert result to list
        result = [recipe_id[0] for recipe_id in result]
        return recipe_id in result
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()

@app.post('/favorite')
def add_favorite(favorite: Favorite):
    values = {
        'user_id': favorite.user_id,
        'recipe_id': favorite.recipe_id
    }
    conn.execute(user_favorite_recipe.insert().values(values))
    return True

@app.delete('/favorite')
def delete_favorite(user_id: int, recipe_id: int):
    conn.execute(user_favorite_recipe.delete().where(and_(user_favorite_recipe.c.user_id == user_id, 
                                                        user_favorite_recipe.c.recipe_id == recipe_id)))
    return True