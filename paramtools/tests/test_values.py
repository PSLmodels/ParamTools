import pytest
import copy

from paramtools.values import Values


@pytest.fixture
def keyfuncs():
    return {"d0": lambda x: x, "d1": lambda x: ["hello", "world"].index(x)}


@pytest.fixture
def _values():
    return [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


@pytest.fixture
def values(_values, keyfuncs):
    return Values(_values, keyfuncs)


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


def test_insert(values):
    copied = copy.deepcopy(values.values)

    new_vals = values.insert([{"d0": 3, "d1": "hello", "value": 1}])

    assert len(values.values) == len(copied)
    assert len(values.index) == len(copied)

    assert len(new_vals.values) == len(copied) + 1
    assert len(new_vals.index) == len(copied) + 1
    assert new_vals.index == [0, 1, 2, 3, 4]

    assert list((new_vals["d0"] == 3) & (new_vals["d1"] == "hello")) == [
        {"d0": 3, "d1": "hello", "value": 1}
    ]


def test_delete(values):
    copied = copy.deepcopy(values.values)

    new_vals = values.delete(0, inplace=False)

    assert len(values.values) == len(copied)
    assert len(values.index) == len(copied)

    assert len(new_vals.values) == len(copied) - 1
    assert len(new_vals.index) == len(copied) - 1
    assert new_vals.index == [1, 2, 3]

    new_vals.delete(1, inplace=True)
    assert len(new_vals.index) == len(copied) - 2
    assert len(new_vals.values) == len(copied) - 2
    assert new_vals.index == [2, 3]


def test_as_values(values):
    queryset = (values["d0"] == 1) | (values["d0"] == 3)
    assert list(queryset) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]

    new_values = queryset.as_values()
    assert list(new_values["d1"] == "hello") == [
        {"d0": 1, "d1": "hello", "value": 1}
    ]
    assert list((new_values["d1"] == "hello") | (new_values["d0"] == 3)) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_select_eq_strict(_values, keyfuncs):
    _values[2]["_auto"] = True
    _values[3]["_auto"] = True
    values = Values(_values, keyfuncs)

    assert list((values["_auto"] == False) | (values.missing("_auto"))) == [
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


def test_isin(values):
    assert list((values["d0"].isin([1, 2])) & (values["d1"] == "hello")) == [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
    ]
