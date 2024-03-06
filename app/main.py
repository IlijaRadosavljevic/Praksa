from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
app = FastAPI()                         # get metoda
                    
my_posts = [{"title": "title of post 3", "content" : "Content of post 3", "id": 3},
            {"title": "title of post 4", "content" : "Content of post   4", "id": 4}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
                    
                                        # uvicorn main:app --reload Pravi live server i monitoruje promene u kodu
@app.get("/")                           # Decorator
async def root():
     
    return {"message": "Welcome to my Python"}  # Funkcija

@app.get("/posts")
async def get_posts():
                                            # Svi postovi
    return {"data": my_posts}

                                # post metoda, pravi se variable payload koji je dictionary json-a iz body-ja postmana.
                                # Mozemo ga direktno printovati ili postovati na ./createposts

#title str, content str
@app.post("/posts",  status_code = status.HTTP_201_CREATED)                              
def create_post(post: Post):
    post_dict = post.dict()                     # Pravljenje postova
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict} 

@app.get("/posts/latest")                       # Uzimanje poslednjeg dodatog posta, mora se staviti iznad pretrazivanja po id jer za vrednost 
                                                #{id} uzima latest koji nije integer
def get_latest_post():
    post = my_posts[len(my_posts)-1]    
    return {"detail" : post}

@app.get("/posts/{id}")         
def get_post(id: int, response: Response):                          # Pretrazivanje postova po id
    post = find_post(id)
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f" Post with id {id} was not found")
    return {"post_detail": post} 


@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int,):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" Post with {id} does not exist")
    my_posts.pop(index)
    return Response(status_code= status.HTTP_204_NO_CONTENT)

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