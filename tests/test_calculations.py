from app.calculations import add


def test_add():
    print("Test")
    sum = add(5,3)
    assert sum==8
