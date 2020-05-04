from paramtools import (
    get_leaves,
    ravel,
    consistent_labels,
    ensure_value_object,
    hashable_value_object,
    filter_labels,
    make_label_str,
    SortedKeyList,
)


def test_get_leaves():
    t = {
        0: {"value": {0: ["leaf1", "leaf2"]}, 1: {"value": {0: ["leaf3"]}}},
        1: {
            "value": {1: ["leaf4", "leaf5"]},
            2: {"value": {0: ["leaf6", ["leaf7", "leaf8"]]}},
        },
    }

    leaves = get_leaves(t)
    assert leaves == [f"leaf{i}" for i in range(1, 9)]

    leaves = get_leaves([t])
    assert leaves == [f"leaf{i}" for i in range(1, 9)]

    leaves = get_leaves({})
    assert leaves == []

    leaves = get_leaves([])
    assert leaves == []

    leaves = get_leaves("leaf")
    assert leaves == ["leaf"]


def test_ravel():
    a = 1
    assert ravel(a) == 1

    b = [1, 2, 3]
    assert ravel(b) == [1, 2, 3]

    c = [[1], 2, 3]
    assert ravel(c) == [1, 2, 3]

    d = [[1, 2, 3], [4, 5, 6]]
    assert ravel(d) == [1, 2, 3, 4, 5, 6]

    e = [0, [1, 2, 3], 4, [5, 6, 7], 8]
    assert ravel(e) == [0, 1, 2, 3, 4, 5, 6, 7, 8]


def test_consistent_labels():
    v = [
        {"label0": 1, "label1": 2, "value": 3},
        {"label0": 4, "label1": 5, "value": 6},
    ]
    assert consistent_labels(v) == set(["label0", "label1"])

    v = [{"label0": 1, "value": 3}, {"label0": 4, "label1": 5, "value": 6}]
    assert consistent_labels(v) is None

    v = [{"label0": 1, "label1": 2, "value": 3}, {"label0": 4, "value": 6}]
    assert consistent_labels(v) is None


def test_ensure_value_object():
    assert ensure_value_object("hello") == [{"value": "hello"}]
    assert ensure_value_object([{"value": "hello"}]) == [{"value": "hello"}]
    assert ensure_value_object([1, 2, 3]) == [{"value": [1, 2, 3]}]
    assert ensure_value_object([[1, 2, 3]]) == [{"value": [[1, 2, 3]]}]
    assert ensure_value_object({"hello": "world"}) == [
        {"value": {"hello": "world"}}
    ]


def test_hashable_value_object():
    assert hash(hashable_value_object({"value": "hello", "world": "!"}))


def test_filter_labels():
    assert filter_labels({"hello": "world"}, drop=["hello"]) == {}
    assert filter_labels({"hello": "world"}, keep=["hello"]) == {
        "hello": "world"
    }
    assert filter_labels({"hello": "world"}) == {"hello": "world"}
    assert filter_labels(
        {"hello": "world", "world": "hello"}, drop=["world"]
    ) == {"hello": "world"}


def test_make_label_str():
    assert make_label_str({"hello": "world", "value": 0}) == "[hello=world]"
    assert make_label_str({"value": 0}) == ""
    assert make_label_str({}) == ""
    assert make_label_str({"b": 0, "c": 1, "a": 2}) == "[a=2, b=0, c=1]"


def test_sorted_key_list():
    [(2, 2), (3, 3), (5, 5), (7, 7)]
    values = {
        "red": 2,
        "blue": 3,
        "orange": 5,
        "white": 6,
        "yellow": 7,
        "green": 9,
        "black": 0,
    }

    to_insert = {"red": 2, "blue": 3, "orange": 5, "yellow": 7}

    skl = SortedKeyList(to_insert, keyfunc=lambda x: values[x])

    assert skl.gte("black") == "red"
    assert skl.lte("black") is None
    skl.insert("black")
    assert skl.gte("black") == "black"
    assert skl.lte("black") == "black"

    assert skl.gte("white") == "yellow"
    assert skl.lte("white") == "orange"
    skl.insert("white")
    assert skl.gte("white") == "white"
    assert skl.lte("white") == "white"

    assert skl.gte("green") is None
    assert skl.lte("green") == "yellow"
    skl.insert("green")
    assert skl.gte("green") == "green"
    assert skl.lte("green") == "green"
