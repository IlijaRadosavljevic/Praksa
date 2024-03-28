from .. import models, schemas, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import desc, func


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@router.get("/", response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("Votes"), models.Comment)
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .join(models.Comment, models.Comment.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id, models.Comment.comment_id)
        .order_by((models.Post.id))
        .all()
    )
 
    posts_list = []
    for post in posts:
        post_item = schemas.Post(
            title=post[0].title,
            content=post[0].content,
            published=post[0].published,
            id=post[0].id,
            created_at=post[0].created_at,
            owner_id=post[0].owner_id,
            owner=post[0].owner,
            comment=[],
            votes_count=post[1]
        )   
        post_item.comment = create_comments(posts, post_id=post[0].id)
        if post_item not in posts_list:
            posts_list.append(post_item)

    return posts_list


@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/latest")
def get_latest_post(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    post = (
        db.query(
            models.Post, func.count(models.Vote.post_id).label("Votes"), models.Comment
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .join(models.Comment, models.Comment.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id, models.Comment.comment_id)
        .order_by(desc(models.Post.created_at))
        .first()
    )
    post_item = schemas.Post(
            title=post[0].title,
            content=post[0].content,
            published=post[0].published,
            id=post[0].id,
            created_at=post[0].created_at,
            owner_id=post[0].owner_id,
            owner=post[0].owner,
            comment=[],
            votes_count=post[1],
        )
    if not post[2]:
        post_item.comment = []
    else: 
        post_item.comment = schemas.Comment(content=post[2].content, user_id=post[2].user_id, post_id=post[2].post_id)

    return post_item


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


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):

    post = (
        db.query(
            models.Post, func.count(models.Vote.post_id).label("Votes"), models.Comment
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .join(models.Comment, models.Comment.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id, models.Comment.comment_id)
        .filter(models.Post.id == id)
        .first()
    )
    comms = (db.query(models.Comment).filter(models.Comment.post_id == id).all())
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} was not found",
        )
    post_item = schemas.Post(
            title=post[0].title,
            content=post[0].content,
            published=post[0].published,
            id=post[0].id,
            created_at=post[0].created_at,
            owner_id=post[0].owner_id,
            owner=post[0].owner,
            comment=[],
            votes_count=post[1],
        )
    if not post[2]:
        post_item.comment = []
    else:
        post_item.comment = comms
    return post_item

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)

    if deleted_post == None or deleted_post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    dp = deleted_post.first().owner_id
    if dp != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perfom action",
        )
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
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
            detail=f"Not authorized to perform action",
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return {"detail":"Post updated successfully"}



def create_comments(posts, post_id):
        comments_list = []
        for post in posts:
            if post[0].id == post_id and post[2]:
                comments_list.append(schemas.Comment(content=post[2].content, user_id=post[2].user_id, post_id=post[2].post_id))
        return comments_list