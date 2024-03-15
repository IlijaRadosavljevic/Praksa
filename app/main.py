from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "https://www.google.com",
]

# Postavljanje CORS-a
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Pokazuje na sve post endopointe u post direktorijumu
app.include_router(post.router)

# Pokazuje na sve user endopointe u user direktorijumu
app.include_router(user.router)

# Pokazuje na sve authentication endopointe u auth direktorijumu
app.include_router(auth.router)

# Pokazuje na sve vote endopointe u vote direktorijumu
app.include_router(vote.router)
