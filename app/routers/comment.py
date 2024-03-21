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
    db: Session = Depends(get_db),
):
    comms = (
        db.query(models.Comment.content).all()
    )
    print(db.query(models.Comment))
    # print(results)
    return comms

@router.post('/')
def comm(comm: schemas.Comment,
         db: Session = Depends(get_db),
         current_user: int = Depends(oauth2.get_current_user)):
    new_comm = models.Comment(user_id = current_user.id, **comm.dict())
    db.add(new_comm)
    db.commit()
    db.refresh(new_comm)
    return new_comm
