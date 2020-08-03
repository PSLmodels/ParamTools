import pytest

from paramtools.select2 import ValueObjects
from paramtools import Parameters


@pytest.fixture
def label_validators():
    schema = {
        "labels": {
            "d0": {
                "type": "int",
                "validators": {"range": {"min": 10, "max": 10}},
            },
            "d1": {
                "type": "str",
                "validators": {"choice": {"choices": ["hello", "world"]}},
            },
        }
    }

    class P(Parameters):
        defaults = {"schema": schema}

    return P().label_validators


@pytest.fixture
def _vos():
    return [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


@pytest.fixture
def vos(_vos, label_validators):
    return ValueObjects(_vos, label_validators)


def test_select_eq(vos):
    assert list((vos["d0"] == 1) & (vos["d1"] == "hello")) == [
        {"d0": 1, "d1": "hello", "value": 1}
    ]
    assert list(
        ((vos["d0"] == 1) | (vos["d0"] == 2)) & (vos["d1"] == "hello")
    ) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_eq_strict(_vos, label_validators):
    _vos[2]["_auto"] = True
    _vos[3]["_auto"] = True
    vos = ValueObjects(_vos, label_validators)
    assert list((vos["_auto"] == False) | (vos.missing("_auto"))) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
    ]


def test_select_ne(vos):
    assert list((vos["d0"] != 1) & (vos["d1"] != "hello")) == [
        {"d0": 3, "d1": "world", "value": 1}
    ]

    assert list((vos["d0"] != 2) & (vos["d0"] != 3)) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
    ]


def test_select_gt(vos):
    assert list(vos["d0"] > 1) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_gte(vos):
    assert list(vos["d0"] >= 2) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_lt(vos):
    assert list(vos["d0"] < 3) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_lte(vos):
    assert list(vos["d0"] <= 2) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]