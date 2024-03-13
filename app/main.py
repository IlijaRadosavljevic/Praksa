from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pravljenje while petlje kako bi se usled neuspele konekcije sa bazon na svake 2 sekunde petlja ponovo izvrsi sve dok se ne ispravi problem.
# Testirao sam sa menjanjem sifre i petlja se izvrasava sve dok nisam ukucao pravilnu sifru i sacuvao
        
# Pokazuje na sve post endopointe u post direktorijumu
app.include_router(post.router)

# Pokazuje na sve user endopointe u user direktorijumu
app.include_router(user.router)

# Pokazuje na sve authentication endopointe u auth direktorijumu
app.include_router(auth.router)
