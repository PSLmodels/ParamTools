from paramtools import utils

def test_get_leaves():
    t = {0: {'value': {0: ['leaf1', 'leaf2']}}}
    r = utils.get_leaves(t)
    assert r == ['leaf1', 'leaf2']