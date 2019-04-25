from paramtools import (
    get_leaves,
    ravel,
    consistent_labels,
    ensure_value_object,
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
