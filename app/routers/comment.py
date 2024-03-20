from .. import models, schemas, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import engine, get_db
from sqlalchemy import desc, func

from app import database


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/")
def get_comms(
    comms: schemas.CommentIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    comms = db.query(models.Comment).all()
    print(db.query(models.Comment))
    # print(results)
    return comms


@router.post("/")
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
    new_comm = models.Comment(user_id=current_user.id, **comm.dict())
    db.add(new_comm)
    db.commit()
    db.refresh(new_comm)
    return new_comm
