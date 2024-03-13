from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency za povezivanje sa bazom
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pravljenje while petlje kako bi se usled neuspele konekcije sa bazon na svake 2 sekunde petlja ponovo izvrsi sve dok se ne ispravi problem.
# Testirao sam sa menjanjem sifre i petlja se izvrasava sve dok nisam ukucao pravilnu sifru i sacuvao

# while True:

#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="fastapi",
#             user="postgres",
#             password="Ilija2002",
#             cursor_factory=RealDictCursor,
#         )
#         cursor = conn.cursor()
#         print("Database connection was succesfull!")
#         break
#     except Exception as e:
#         print("Database connection failed :(")
#         print("Error: ", e)
#         time.sleep(2)