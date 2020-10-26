import pytest
import copy

from paramtools.values import Values, Slice, QueryResult, ValueItem


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


class TestValues:
    def test_values(self, values):
        assert len(values) == 4

    def test_key_error(self, values):
        with pytest.raises(KeyError):
            values["heyo"]

    def test_types(self, values):
        assert isinstance(values["d0"], Slice)

        assert isinstance(values["d0"] > 1, QueryResult)

        qr = values["d0"] > 1
        assert isinstance(qr.isel[0], dict)
        assert isinstance(qr.isel[:], list)

        assert isinstance(values.isel, ValueItem)

        assert isinstance(qr.as_values(), Values)


class TestQuery:
    def test_select_eq(self, values):
        assert list((values["d0"] == 1) & (values["d1"] == "hello")) == [
            {"d0": 1, "d1": "hello", "value": 1}
        ]
        assert list(
            ((values["d0"] == 1) | (values["d0"] == 2))
            & (values["d1"] == "hello")
        ) == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 2, "d1": "hello", "value": 1},
        ]

    def test_select_eq_strict(self, _values, keyfuncs):
        _values[2]["_auto"] = True
        _values[3]["_auto"] = True
        values = Values(_values, keyfuncs)

        assert list(
            (values["_auto"] == False) | (values.missing("_auto"))
        ) == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 1, "d1": "world", "value": 1},
        ]

    def test_select_ne(self, values):
        assert list((values["d0"] != 1) & (values["d1"] != "hello")) == [
            {"d0": 3, "d1": "world", "value": 1}
        ]

        assert list((values["d0"] != 2) & (values["d0"] != 3)) == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 1, "d1": "world", "value": 1},
        ]

    def test_select_gt(self, values):
        assert list(values["d0"] > 1) == [
            {"d0": 2, "d1": "hello", "value": 1},
            {"d0": 3, "d1": "world", "value": 1},
        ]

    def test_select_gte(self, values):
        assert list(values["d0"] >= 2) == [
            {"d0": 2, "d1": "hello", "value": 1},
            {"d0": 3, "d1": "world", "value": 1},
        ]

    def test_select_lt(self, values):
        assert list(values["d0"] < 3) == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 1, "d1": "world", "value": 1},
            {"d0": 2, "d1": "hello", "value": 1},
        ]

    def test_select_lte(self, values):
        assert list(values["d0"] <= 2) == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 1, "d1": "world", "value": 1},
            {"d0": 2, "d1": "hello", "value": 1},
        ]

    def test_isin(self, values):
        assert list(
            (values["d0"].isin([1, 2])) & (values["d1"] == "hello")
        ) == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 2, "d1": "hello", "value": 1},
        ]


class TestOperations:
    def test_add(self, values):
        copied = copy.deepcopy(values.values)

        new_vals = values.add([{"d0": 3, "d1": "hello", "value": 1}])

        assert len(values.values) == len(copied)
        assert len(values.index) == len(copied)

        assert len(new_vals.values) == len(copied) + 1
        assert len(new_vals.index) == len(copied) + 1
        assert new_vals.index == [0, 1, 2, 3, 4]

        assert list((new_vals["d0"] == 3) & (new_vals["d1"] == "hello")) == [
            {"d0": 3, "d1": "hello", "value": 1}
        ]

    def test_delete(self, values):
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

    def test_as_values(self, values):
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
        assert list(
            (new_values["d1"] == "hello") | (new_values["d0"] == 3)
        ) == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 3, "d1": "world", "value": 1},
        ]


class TestIndexing:
    def test_Values(self, values, _values):
        for ix, value in enumerate(_values):
            assert values.isel[ix] == _values[ix]

    def test_Slice(self, values, _values):
        for ix, value in enumerate(_values):
            assert values["d0"][ix] == _values[ix]["d0"]

    def test_QueryResult(self, values):
        res1 = (values["d0"] == 1) & (values["d1"] == "hello")

        assert res1.isel[0] == {"d0": 1, "d1": "hello", "value": 1}

        res2 = ((values["d0"] == 1) | (values["d0"] == 2)) & (
            values["d1"] == "hello"
        )
        assert list(res2) == res2.isel[:2]
        assert res2.isel[:2] == [
            {"d0": 1, "d1": "hello", "value": 1},
            {"d0": 2, "d1": "hello", "value": 1},
        ]
        assert res2.isel[0] == {"d0": 1, "d1": "hello", "value": 1}
        assert res2.isel[1] == {"d0": 2, "d1": "hello", "value": 1}

    def test_not_implemented(self, values):
        with pytest.raises(NotImplementedError):
            values["d0"].isel[0]

        with pytest.raises(NotImplementedError):
            (values["d0"] == 1)[0]
