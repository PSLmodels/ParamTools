import copy
import pytest
import numpy as np

from paramtools.exceptions import ParamToolsError
from paramtools.select import eq_func
from paramtools.tree import Tree


@pytest.fixture
def vos():
    return [
        {"d0": 1, "d1": "hello", "value": 1},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


@pytest.fixture
def label_grid():
    return {
        "d0": list(range(0, 10)),
        "d1": ["hello", "world"],
        "d2": list(range(0, 5)),
    }


def assert_rebalanced(tree):
    exp_tree = Tree(copy.deepcopy(tree.vos), tree.label_grid)

    tree.init()
    exp_tree.init()

    np.testing.assert_equal(tree.tree, exp_tree.tree)


def test_init(vos, label_grid):
    assert Tree(vos, label_grid)


def test_build(vos, label_grid):
    tree = Tree(vos, label_grid)
    tree.init()
    exp_tree = {
        "d0": {1: {0, 1}, 2: {2}, 3: {3}},
        "d1": {"hello": {0, 2}, "world": {1, 3}},
    }
    np.testing.assert_equal(tree.tree, exp_tree)


def test_update_simple(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [{"d0": 1, "d1": "hello", "value": 2}]
    new_tree = Tree(new_vos, label_grid)
    tree.update(new_tree)
    assert tree.vos == [
        {"d0": 1, "d1": "hello", "value": 2},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]
    assert_rebalanced(tree)


def test_update_all(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [
        {"d0": 1, "d1": "hello", "value": 2},
        {"d0": 1, "d1": "world", "value": 3},
        {"d0": 2, "d1": "hello", "value": 4},
        {"d0": 3, "d1": "world", "value": 5},
    ]
    new_tree = Tree(new_vos, label_grid)
    tree.update(new_tree)
    assert tree.vos == [
        {"d0": 1, "d1": "hello", "value": 2},
        {"d0": 1, "d1": "world", "value": 3},
        {"d0": 2, "d1": "hello", "value": 4},
        {"d0": 3, "d1": "world", "value": 5},
    ]
    assert_rebalanced(tree)


def test_update_one_label(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [{"d1": "hello", "value": 2}]
    new_tree = Tree(new_vos, label_grid)
    tree.update(new_tree)
    assert tree.vos == [
        {"d0": 1, "d1": "hello", "value": 2},
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 2, "d1": "hello", "value": 2},
        {"d0": 3, "d1": "world", "value": 1},
    ]
    assert_rebalanced(tree)


def test_update_no_labels(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [{"value": 2}]
    new_tree = Tree(new_vos, label_grid)
    tree.update(new_tree)
    assert tree.vos == [
        {"d0": 1, "d1": "hello", "value": 2},
        {"d0": 1, "d1": "world", "value": 2},
        {"d0": 2, "d1": "hello", "value": 2},
        {"d0": 3, "d1": "world", "value": 2},
    ]
    assert_rebalanced(tree)


def test_delete_some(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [{"d1": "hello", "value": None}]
    new_tree = Tree(new_vos, label_grid)
    tree.update(new_tree)
    assert tree.vos == [
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]


def test_delete_all(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [{"value": None}]
    new_tree = Tree(new_vos, label_grid)
    tree.update(new_tree)
    assert tree.vos == []
    assert_rebalanced(tree)


def test_delete_some_update_some(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [{"d1": "hello", "value": None}, {"d1": "world", "value": 4}]
    new_tree = Tree(new_vos, label_grid)
    tree.update(new_tree)
    assert tree.vos == [
        {"d0": 1, "d1": "world", "value": 4},
        {"d0": 3, "d1": "world", "value": 4},
    ]
    assert_rebalanced(tree)


def test_error_on_extra_label(vos, label_grid):
    tree = Tree(vos, label_grid)
    new_vos = [{"d2": 2, "d0": 1, "d1": "hello", "value": 2}]
    new_tree = Tree(new_vos, label_grid)
    with pytest.raises(ParamToolsError):
        tree.update(new_tree)
    assert_rebalanced(tree)


def test_select(vos, label_grid):
    tree = Tree(vos, label_grid)

    res = tree.select({}, eq_func)
    assert res == vos

    res = tree.select({"d1": "world"}, eq_func)
    assert res == [
        {"d0": 1, "d1": "world", "value": 1},
        {"d0": 3, "d1": "world", "value": 1},
    ]

    res = tree.select({"d0": 1, "d1": "world"}, eq_func)
    assert res == [{"d0": 1, "d1": "world", "value": 1}]

    assert tree.select({"d2": 1}, eq_func, strict=True) == []
