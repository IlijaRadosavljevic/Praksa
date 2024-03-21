from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db
from app.main import app
from app.database import Base
import pytest
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:Ilija2002@localhost:5432/fastapi_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Test_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixtura za povezivanje sa bazom
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Test_SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pravljenje obicnog korisnika kome prosledjuemo db iz session fixture
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# Pravljenje korsnika za testiranje
@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "hello123345@gmail.com", "password": "password123345"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


# Fixture za pravljenje tokena
@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


# Autentifikujemo korisnike za testiranje
@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


# Pravi se postovi za testiranje i automatski se prave i test korisnici
@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {
            "title": "first title",
            "content": "firsto content",
            "owner_id": test_user["id"],
        },
        {
            "title": "second title",
            "content": "second content",
            "owner_id": test_user["id"],
        },
        {
            "title": "third title",
            "content": "third content",
            "owner_id": test_user["id"],
        },
        {
            "title": "fourth title",
            "content": "fourth content",
            "owner_id": test_user2["id"],
        },
    ]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)

    posts = list(post_map)

    session.add_all(posts)
    # Da ne bi hardcode-ovali ovo mozemo da napravimo postove preko mape
    # session.add_all([models.Post(title='first title', content='firsto content', owner_id= test_user['id']),
    #                  models.Post(title='second title', content='second content', owner_id= test_user['id']),
    #                  models.Post(title='third title', content='third content', owner_id= test_user['id'])])
    session.commit()

    posts = session.query(models.Post).all()

    return posts


@pytest.fixture
def test_comments(test_user, session, test_user2):
    comments_data = [
        {
            "user_id": test_user2["id"],
            "content": "firsto content",
        },
        {
            "user_id": test_user["id"],
            "content": "firsto content",
        },
        {
            "user_id": test_user["id"],
            "content": "firsto content",
        },
        {
            "user_id": test_user["id"],
            "content": "firsto content",
        },
    ]

    def create_comment_model(post):
        return models.Comment(**post)

    post_map = map(create_comment_model, comments_data)

    comments = list(post_map)

    session.add_all(comments)
    session.commit()

    comments = session.query(models.Comment).all()

    return comments
