import pytest

from paramtools.values import Values
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
def _values():
    return [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


@pytest.fixture
def values(_values, label_validators):
    return Values(_values, label_validators)


def test_select_eq(values):
    assert list((values["d0"] == 1) & (values["d1"] == "hello")) == [
        {"d0": 1, "d1": "hello", "value": 1}
    ]
    assert list(
        ((values["d0"] == 1) | (values["d0"] == 2)) & (values["d1"] == "hello")
    ) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_eq_strict(_values, label_validators):
    _values[2]["_auto"] = True
    _values[3]["_auto"] = True
    values = Values(_values, label_validators)

    assert list(
        (values["_auto"] == False) | (values.missing("_auto"))  # noqa: E712
    ) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
    ]


def test_select_ne(values):
    assert list((values["d0"] != 1) & (values["d1"] != "hello")) == [
        {"d0": 3, "d1": "world", "value": 1}
    ]

    assert list((values["d0"] != 2) & (values["d0"] != 3)) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
    ]


def test_select_gt(values):
    assert list(values["d0"] > 1) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_gte(values):
    assert list(values["d0"] >= 2) == [
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_lt(values):
    assert list(values["d0"] < 3) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]


def test_select_lte(values):
    assert list(values["d0"] <= 2) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]
