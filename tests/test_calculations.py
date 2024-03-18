from app.calculations import add


def test_add():
    print("Test")
    assert add(5,3) == 8
