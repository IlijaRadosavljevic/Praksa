from .. import models, schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from ..database import engine, get_db
from sqlalchemy import desc

router = APIRouter(prefix="/posts", tags=["Posts"])


# Test endpoint za pristup bazi podataka preko Pytona bez direktnih SQL query-ja
@router.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


# Modifikovani endpoint
@router.get("/", response_model=List[schemas.Post])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


# Post metoda, pravi se variable payload koji je dictionary json-a iz body-ja postmana.
# Mozemo ga direktno printovati ili postovati na ./createposts
# Prosledjivanje podataka u postgres
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# Uzimanje poslednjeg dodatog posta, mora se staviti iznad pretrazivanja po id jer za vrednost
# {id} uzima latest koji nije integer
# Prikazati najnoviji post uz pomoc SQLAlchemy
@router.get("/latest")
def get_latest_post(db: Session = Depends(get_db)):
    l_post = db.query(models.Post).order_by(desc("created_at")).first()
    return {"detail": l_post}


# Prikaz svih unetih postova koji sadrze unetu rec u title
@router.get("/title/{tmp}", response_model=list[schemas.Post])
def get_posts(tmp: str, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.title.contains(tmp)).all()
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with title {tmp} was not found",
        )
    return post


# Pretrazivanje postova po id
@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} was not found",
        )
    return post


# Brisanje posta koji ima uneti id
# Dodatno brisanje pretrazenog id-a iz baze podataka
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post == None or deleted_post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Azuriranje posta koji ima uneti id
# Dodatno azuriranje baze podataka
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    pos = post_query.first()
    if pos == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
