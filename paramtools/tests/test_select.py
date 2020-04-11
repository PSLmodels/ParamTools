import pytest

from paramtools.select import (
    select_eq,
    select_gt,
    select_gte,
    select_lt,
    select_lte,
)


@pytest.fixture
def vos():
    return [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_eq(vos):
    assert list(select_eq(vos, True, labels={"d0": 1, "d1": "hello"})) == [
        {"d0": 1, "d1": "hello", "value": 1}
    ]

    assert list(
        select_eq(vos, True, labels={"d0": [1, 2], "d1": "hello"})
    ) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_gt(vos):
    assert list(select_gt(vos, True, labels={"d0": 1})) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_gte(vos):
    assert list(select_gte(vos, True, labels={"d0": 2})) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_lt(vos):
    assert list(select_lt(vos, True, labels={"d0": 3})) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_lte(vos):
    assert list(select_lte(vos, True, labels={"d0": 2})) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]
