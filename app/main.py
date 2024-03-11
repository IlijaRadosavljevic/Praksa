from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .routers import post, user


models.Base.metadata.create_all(bind = engine)

app = FastAPI()


my_posts = [
    {"title": "title of post 3", "content": "Content of post 3", "id": 3},
    {"title": "title of post 4", "content": "Content of post   4", "id": 4},
]


# Funkcija za pretragu posta sa unetim id-om
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


# Funkcija za pretragu indexa posta koji ima uneti id
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i




# Pravljenje while petlje kako bi se usled neuspele konekcije sa bazon na svake 2 sekunde petlja ponovo izvrsi sve dok se ne ispravi problem.
# Testirao sam sa menjanjem sifre i petlja se izvrasava sve dok nisam ukucao pravilnu sifru i sacuvao
while True:

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="Ilija2002",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was succesfull!")
        break
    except Exception as e:
        print("Database connection failed :(")
        print("Error: ", e)
        time.sleep(2)

        
# Pokazuje na sve post endopointe u post folderu
app.include_router(post.router) 

# Pokazuje na sve user endopointe u user folderu
app.include_router(user.router)