from paramtools import utils


def test_get_leaves():
    t = {
        0: {"value": {0: ["leaf1", "leaf2"]}, 1: {"value": {0: ["leaf3"]}}},
        1: {
            "value": {1: ["leaf4", "leaf5"]},
            2: {"value": {0: ["leaf6", ["leaf7", "leaf8"]]}},
        },
    }

    gl = utils.LeafGetter()
    gl.get(t)
    assert gl.leaves == [f"leaf{i}" for i in range(1, 9)]

    gl = utils.LeafGetter()
    gl.get([t])
    assert gl.leaves == [f"leaf{i}" for i in range(1, 9)]

    gl = utils.LeafGetter()
    gl.get({})
    assert gl.leaves == []

    gl = utils.LeafGetter()
    gl.get([])
    assert gl.leaves == []

    gl = utils.LeafGetter()
    gl.get("leaf")
    assert gl.leaves == ["leaf"]

    gl.clear()
    assert gl.leaves == []
