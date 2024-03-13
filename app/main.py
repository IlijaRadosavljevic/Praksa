from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


        
# Pokazuje na sve post endopointe u post direktorijumu
app.include_router(post.router)

# Pokazuje na sve user endopointe u user direktorijumu
app.include_router(user.router)

# Pokazuje na sve authentication endopointe u auth direktorijumu
app.include_router(auth.router)
