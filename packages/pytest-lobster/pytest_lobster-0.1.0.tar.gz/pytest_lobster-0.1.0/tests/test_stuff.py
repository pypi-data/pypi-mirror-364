import pytest


def test_true():
    assert True

def test_false():
    assert False

@pytest.mark.skip(reason="Just for fun")
def test_skip():
    assert True
