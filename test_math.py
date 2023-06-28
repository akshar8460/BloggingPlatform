from main import add, diff


def test_add():
    assert add(1, 2) == {"sum": 3}
    assert add(-1, 2) == {"sum": 1}
    assert add(1, -2) == {"sum": -1}
    assert add(-1, -2) == {"sum": -3}
    assert add(1, 0) == {"sum": 1}


def test_diff():
    assert diff(1, 2) == {"diff": -1}
    assert diff(-1, 2) == {"diff": -3}
    assert diff(1, -2) == {"diff": 3}
    assert diff(-1, -2) == {"diff": 1}
    assert diff(1, 0) == {"diff": 1}
