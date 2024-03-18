from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db
from app.main import app
from app.database import Base
import pytest
 
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:Ilija2002@localhost:5432/fastapi_test" 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Test_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Test_SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    