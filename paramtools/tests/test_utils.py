import os
import pytest

from paramtools import (
    get_leaves,
    ravel,
    consistent_labels,
    ensure_value_object,
    hashable_value_object,
    filter_labels,
    make_label_str,
    read_json,
)


class TestRead:
    @pytest.mark.network_bound
    def test_read_s3(self):
        res = read_json("s3://paramtools-test/defaults.json", {"anon": True})
        assert isinstance(res, dict)

    @pytest.mark.network_bound
    def test_read_gcp(self):
        res = read_json("gs://paramtools-dev/defaults.json", {"token": "anon"})
        assert isinstance(res, dict)

    @pytest.mark.network_bound
    def test_read_http(self):
        http_path = (
            "https://raw.githubusercontent.com/PSLmodels/ParamTools/master/"
            "paramtools/tests/defaults.json"
        )
        res = read_json(http_path)
        assert isinstance(res, dict)

    @pytest.mark.network_bound
    def test_read_github(self):
        gh_path = "github://PSLmodels:ParamTools@master/paramtools/tests/defaults.json"
        res = read_json(gh_path)
        assert isinstance(res, dict)

    def test_read_file_path(self):
        CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
        defaults_path = os.path.join(CURRENT_PATH, "defaults.json")
        res = read_json(defaults_path)
        assert isinstance(res, dict)

    def test_read_string(self):
        res = read_json('{"hello": "world"}')
        assert isinstance(res, dict)

    def test_read_invalid(self):
        with pytest.raises(ValueError):
            read_json('{"hello": "world"')

        with pytest.raises(ValueError):
            read_json(f":{['a'] * 200}")

        with pytest.raises(TypeError):
            read_json(("hello", "world"))

        with pytest.raises(TypeError):
            read_json(None)

    def test_strip_comments_simple(self):
        """test strip comment"""
        params = """
        // my comment
        // another
        {
            "hello": "world"
        }
        """
        assert read_json(params) == {"hello": "world"}

    def test_strip_comments_multiline(self):
        """test strip comment"""
        params = """
        /* my comment
        another
        */
        {
            "hello": "world"
        }
        """
        assert read_json(params) == {"hello": "world"}

    def test_strip_comments_ignores_url(self):
        """test strips comment but doesn't affect http://..."""
        params = """
        // my comment
        {
            "hello": "http://world"
        }
        """
        assert read_json(params) == {"hello": "http://world"}


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
