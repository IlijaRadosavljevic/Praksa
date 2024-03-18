from app.calculations import add, substract, multiply, divide, BankAccount

import pytest

@pytest.fixture
def zero_ba():
    return BankAccount(0)

@pytest.fixture
def ba():
    return BankAccount(50)


@pytest.mark.parametrize("num1, num2, expected", [
    (3,2,5),
    (7,1,8),
    (12,4,16)
])
def test_add(num1, num2, expected):
    assert add(num1,num2) == expected

def test_substract():
    assert substract(5,3) == 2

def test_divide():
    assert divide(6,3) == 2

def test_multiply():
    assert multiply(5,3) == 15

def test_bank_set_initial_amount(ba):
    assert ba.balance == 50

def test_bank_def(zero_ba):
    assert zero_ba.balance == 0

def test_withdraw(ba):
    ba.withdraw(20)
    assert ba.balance == 30 

def test_deposit(ba):
    ba.deposit(20)
    assert ba.balance == 70 

def test_collect_interest(ba):
    ba.collect_interest()
    assert round(ba.balance) == 55

@pytest.mark.parametrize("deposited, withdrew, expected", [
    (200,100,100),
    (50,10,40),
    (1200,200,1000),
    # (500,700,-200)
])
def test_bank_transaction(zero_ba, deposited, withdrew, expected):
    zero_ba.deposit(deposited)
    zero_ba.withdraw(withdrew)
    assert zero_ba.balance == expected

def test_ins_funds(ba):
    with pytest.raises(Exception):
        ba.withdraw(70)