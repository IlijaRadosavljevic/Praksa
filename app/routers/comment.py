from .. import models, schemas, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from ..database import engine, get_db


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/", response_model=List[schemas.Comment])
def get_comms(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    comms = db.query(models.Comment).all()
    return comms


@router.get("/{id}", response_model=schemas.Comment)
def get_one_comm(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    comm = db.query(models.Comment).filter(models.Comment.comment_id == id).first()

    if not comm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Comment with id {id} was not found",
        )

    return comm


@router.post("/", response_model=schemas.Comment)
def comm(
    comm: schemas.CommentIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == comm.post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {comm.post_id} does not exist",
        )
    new_comm = models.Comment(user_id=current_user.id, **comm.model_dump())
    db.add(new_comm)
    db.commit()
    db.refresh(new_comm)
    return new_comm


@router.delete("/{id}")
def delete_comm(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    comment = db.query(models.Comment).filter(models.Comment.comment_id == id)

    if comment == None or comment.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Post with id {id} does not exist",
        )
    dc = comment.first().user_id
    if dc != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perfom action",
        )

    comment.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Comment)
def update_comm(
    id: int,
    comm: schemas.CommentBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    comment = db.query(models.Comment).filter(models.Comment.comment_id == id)
    if comment.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Comment with id {id} does not exist",
        )
    if comment.first().user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform action",
        )
    comment.update(comm.model_dump(), synchronize_session=False)
    db.commit()
    return comment.first()
