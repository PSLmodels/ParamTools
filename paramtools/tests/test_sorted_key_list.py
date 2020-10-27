import pytest
from paramtools.sorted_key_list import SortedKeyList, SortedKeyListException


def test_sorted_key_list():
    values = {
        "red": 2,
        "blue": 3,
        "orange": 5,
        "white": 6,
        "yellow": 7,
        "green": 9,
        "black": 0,
    }

    to_add = ["red", "blue", "orange", "yellow"]

    skl = SortedKeyList(
        to_add, keyfunc=lambda x: values[x], index=list(range(len(to_add)))
    )

    assert skl.eq("black") is None
    assert skl.gte("black").values[0] == "red"
    assert skl.lte("black") is None
    skl.add("black")
    assert skl.gte("black").values[0] == "black"
    assert skl.lte("black").values[-1] == "black"
    assert skl.eq("black").values == ["black"]

    assert skl.gte("white").values[0] == "yellow"
    assert skl.lte("white").values[-1] == "orange"
    skl.add("white")
    assert skl.gte("white").values[0] == "white"
    assert skl.gt("white").values[0] == "yellow"
    assert skl.lte("white").values[-1] == "white"
    assert skl.lt("yellow").values[-1] == "white"

    assert skl.gte("green") is None
    assert skl.lte("green").values[-1] == "yellow"
    skl.add("green")
    assert skl.gte("green").values[0] == "green"
    assert skl.lte("green").values[-1] == "green"

    skl.add("green")
    assert skl.eq("green").values == ["green", "green"]

    assert set(skl.ne("green").values) == set(list(values.keys())) - {"green"}
    values["pokadot"] = -1
    assert set(skl.ne("pokadot").values) == set(list(values.keys())) - {
        "pokadot"
    }


def test_exception():
    with pytest.raises(SortedKeyListException):
        SortedKeyList(
            [
                {"really": {"nested": {"field": True}}},
                {"really": {"nested": {"field": False}}},
            ],
            keyfunc=lambda x: x,
        )
