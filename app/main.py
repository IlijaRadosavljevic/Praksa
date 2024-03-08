from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import desc



models.Base.metadata.create_all(bind = engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

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


# Pravljenje objekta klase Post
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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


# Pocetna poruka
@app.get("/")
async def root():
    return {"message": "Welcome to my Python"}

# Test endpoint za pristup bazi podataka preko Pytona bez direktnih SQL query-ja
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return{"data": posts}



# Modifikovani endpoint
@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


# Post metoda, pravi se variable payload koji je dictionary json-a iz body-ja postmana.
# Mozemo ga direktno printovati ili postovati na ./createposts
# Prosledjivanje podataka u postgres
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    ### new_post=models.Post(title=post.title, content=post.content, published=post.published) ###
    new_post=models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


# Uzimanje poslednjeg dodatog posta, mora se staviti iznad pretrazivanja po id jer za vrednost
# {id} uzima latest koji nije integer
# Prikazati najnoviji post uz pomoc SQLAlchemy
@app.get("/posts/latest")
def get_latest_post(db: Session = Depends(get_db)):
    l_post = db.query(models.Post).order_by(desc('created_at')).first()
    # cursor.execute(
    #     """SELECT * FROM posts where created_at=( SELECT MAX(created_at) FROM posts)"""
    # )
    # l_post = cursor.fetchone()
    return {"detail": l_post}


# Pretrazivanje postova po id
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts where id = %s """, str(id))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} was not found",
        )
    return {"post_detail": post}


# Brisanje posta koji ima uneti id
# Dodatno brisanje pretrazenog id-a iz baze podataka
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where id = %s  RETURNING *""", str(id))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post.first() == None or deleted_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    deleted_post.delete(synchronize_session=False)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Azuriranje posta koji ima uneti id
# Dodatno azuriranje baze podataka
@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #     (post.title, post.content, post.published, str(id)),
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    pos= post_query.first()
    if pos == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {"data": post_query.first()}


@app.patch("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s  WHERE id = %s RETURNING *""",
        (post.title, str(id)),
    )
    updat_post = cursor.fetchone()
    conn.commit()
    if updat_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    return {"data": updat_post}
