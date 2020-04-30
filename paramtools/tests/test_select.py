import pytest

from paramtools.select import (
    select_eq,
    select_ne,
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
    assert list(select_eq(vos, False, labels={"d0": 1, "d1": "hello"})) == [
        {"d0": 1, "d1": "hello", "value": 1}
    ]

    assert list(
        select_eq(vos, False, labels={"d0": [1, 2], "d1": "hello"})
    ) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_eq_strict(vos):
    assert list(select_eq(vos, True, labels={"d0": 1, "d1": "hello"})) == [
        {"d0": 1, "d1": "hello", "value": 1}
    ]

    assert list(
        select_eq(vos, True, labels={"d0": [1, 2], "d1": "hello"})
    ) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]

    vos[2]["_auto"] = True
    vos[3]["_auto"] = True
    assert list(select_eq(vos, False, labels={"_auto": False})) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
    ]


def test_select_ne(vos):
    assert list(select_ne(vos, False, labels={"d0": 1, "d1": "hello"})) == [
        {"d0": 3, "d1": "world", "value": 1}
    ]

    assert list(select_ne(vos, False, labels={"d0": [2, 3]})) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
    ]


def test_select_gt(vos):
    assert list(select_gt(vos, False, labels={"d0": 1})) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_gte(vos):
    assert list(select_gte(vos, False, labels={"d0": 2})) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_lt(vos):
    assert list(select_lt(vos, False, labels={"d0": 3})) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_lte(vos):
    assert list(select_lte(vos, False, labels={"d0": 2})) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]
