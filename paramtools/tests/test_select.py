import pytest

from paramtools.select import select_eq, select_ne


@pytest.fixture
def vos():
    return [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_eq(vos):
    assert select_eq(vos, True, labels={"d0": 1, "d1": "hello"}) == [
        {"d0": 1, "d1": "hello", "value": 1}
    ]

    assert select_eq(vos, True, labels={"d0": [1, 2], "d1": "hello"}) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_ne(vos):
    assert select_ne(vos, True, labels={"d0": 1, "d1": "hello"}) == [
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]

    assert select_ne(vos, True, labels={"d0": [1, 2], "d1": "hello"}) == [
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]
