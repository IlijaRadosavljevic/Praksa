from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
app = FastAPI()                         

                    
my_posts = [{"title": "title of post 3", "content" : "Content of post 3", "id": 3},
            {"title": "title of post 4", "content" : "Content of post   4", "id": 4}]

# Funkcija za pretragu posta sa unetim id-om
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
# Funkcija za pretragu indexa posta koji ima uneti id
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
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
        conn = psycopg2.connect(host= 'localhost', database='fastapi', user='postgres', password='Ilija2002', cursor_factory= RealDictCursor)
        cursor = conn.cursor()
        print('Database connection was succesfull!')
        break
    except Exception as e:
        print('Database connection failed :(')
        print("Error: ", e)
        time.sleep(2)

                    
# Pocetna poruka
@app.get("/")                           
async def root():
    return {"message": "Welcome to my Python"}

# Prikaz svih postova pomocu get metode
@app.get("/posts")
async def get_posts():
                                            
    return {"data": my_posts}

# Post metoda, pravi se variable payload koji je dictionary json-a iz body-ja postmana.
# Mozemo ga direktno printovati ili postovati na ./createposts
@app.post("/posts",  status_code = status.HTTP_201_CREATED)                              
def create_post(post: Post):
    post_dict = post.dict()                                         # Pravljenje postova
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict} 

# Uzimanje poslednjeg dodatog posta, mora se staviti iznad pretrazivanja po id jer za vrednost 
# {id} uzima latest koji nije integer
@app.get("/posts/latest")                       
def get_latest_post():
    post = my_posts[len(my_posts)-1]    
    return {"detail" : post}

# Pretrazivanje postova po id
@app.get("/posts/{id}")         
def get_post(id: int, response: Response):                          
    post = find_post(id)
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f" Post with id {id} was not found")
    return {"post_detail": post} 

# Brisanje posta koji ima uneti id
@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int,):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" Post with {id} does not exist")
    my_posts.pop(index)
    return Response(status_code= status.HTTP_204_NO_CONTENT)

# Azuriranje posta koji ima uneti id
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    print(post)
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" Post with {id} does not exist")
    post_dict = post.dict()
    post_dict['id'] = id 
    my_posts[index] = post_dict
    return {'post': post_dict}

