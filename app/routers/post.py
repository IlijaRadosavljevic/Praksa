from .. import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import engine, get_db
from sqlalchemy import desc, func

router = APIRouter(prefix="/posts", tags=["Posts"])


# Test endpoint za pristup bazi podataka preko Pytona bez direktnih SQL query-ja
@router.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


# Modifikovani endpoint
@router.get("/", response_model=List[schemas.Post])
async def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):

    posts = (
        db.query(models.Post)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts


# Post metoda, pravi se variable payload koji je dictionary json-a iz body-ja postmana.
# Mozemo ga direktno printovati ili postovati na ./createposts
# Prosledjivanje podataka u postgres
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# Uzimanje poslednjeg dodatog posta, mora se staviti iznad pretrazivanja po id jer za vrednost
# {id} uzima latest koji nije integer
# Prikazati najnoviji post uz pomoc SQLAlchemy
@router.get("/latest")
def get_latest_post(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    l_post = db.query(models.Post).order_by(desc("created_at")).first()
    return {"detail": l_post}


@router.get("/test")
def test_func(db: Session = Depends(get_db)):
    pos = db.query(models.Post.title).filter(models.Post.id < 15).all()
    if pos == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return pos


@router.get("/second")
def test_func(db: Session = Depends(get_db)):
    pos = (
        db.query(func.concat(models.Post.id, " ", models.Post.content).label("Novo"))
        .limit(3)
        .all()
    )
    if pos == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return pos


# Prikaz svih unetih postova koji sadrze unetu rec u title
@router.get("/title/{tmp}", response_model=List[schemas.Post])
def get_posts(
    tmp: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
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
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    dp = deleted_post.first().owner_id

    if deleted_post == None or deleted_post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    if dp != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perfom action",
        )
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Azuriranje posta koji ima uneti id
# Dodatno azuriranje baze podataka
@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    pos = post_query.first()
    if pos == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    if pos.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perfom action",
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
