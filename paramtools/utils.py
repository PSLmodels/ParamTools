import json
import os
from collections import OrderedDict
from typing import List

from paramtools.typing import ValueObject


def read_json(path):
    """
    Read JSON file shortcut
    """
    if isinstance(path, str) and os.path.exists(path):
        with open(path, "r") as f:
            r = json.loads(f.read(), object_pairs_hook=OrderedDict)
        return r
    elif isinstance(path, dict):
        return path
    else:
        return json.loads(path)


def get_example_paths(name):
    assert name in ("taxparams-demo",)
    current_path = os.path.abspath(os.path.dirname(__file__))
    default_spec_path = os.path.join(
        current_path, f"examples/{name}/defaults.json"
    )
    return default_spec_path


class LeafGetter:
    """
    Return all non-dict or non-list items of a given object. This object
    should be an item or a list or dictionary composed of non-iterable items,
    nested dictionaries or nested lists.

    A functional approach was considered instead of this class. However, I was
    unable to come up with a way to store all of the leaves without "cheating"
    and keeping "leaf" state.
    """

    def __init__(self):
        self.leaves = []

    def get(self, item):
        if isinstance(item, dict):
            for _, v in item.items():
                self.get(v)
        elif isinstance(item, list):
            for li in item:
                self.get(li)
        else:
            self.leaves.append(item)


def get_leaves(item):
    gl = LeafGetter()
    gl.get(item)
    return gl.leaves


def ravel(nlabel_list):
    """ only up to 2D for now. """
    if not isinstance(nlabel_list, list):
        return nlabel_list
    raveled = []
    for maybe_list in nlabel_list:
        if isinstance(maybe_list, list):
            for item in maybe_list:
                raveled.append(item)
        else:
            raveled.append(maybe_list)
    return raveled


def consistent_labels(value_items: List[ValueObject]):
    """
    Get labels used consistently across all value objects.
    Returns None if labels are omitted or added for
    some value object(s).
    """
    if not value_items:
        return set([])
    used = set(k for k in value_items[0] if k != "value")
    for vo in value_items:
        if used != set(k for k in vo if k != "value"):
            return None
    return used


def ensure_value_object(vo) -> ValueObject:
    if not isinstance(vo, list) or (
        isinstance(vo, list) and not isinstance(vo[0], dict)
    ):
        vo = [{"value": vo}]
    return vo


def hashable_value_object(vo: ValueObject) -> tuple:
    """
    Helper function convertinga value object into a format
    that can be stored in a set.
    """
    return tuple(sorted(vo.items()))


def filter_labels(vo: ValueObject, drop=None, keep=None) -> ValueObject:
    """
    Filter a value objects labels by keeping labels
    in keep if specified and dropping labels that are in drop.
    """
    drop = drop or ()
    keep = keep or ()
    return {
        l: lv
        for l, lv in vo.items()
        if (l not in drop) and (not keep or l in keep)
    }


def make_label_str(vo: ValueObject) -> str:
    """
    Create string from labels. This is used to create error messages.
    """
    lab_str = ", ".join(
        [f"{lab}={vo[lab]}" for lab in sorted(vo) if lab != "value"]
    )
    if lab_str:
        return f"[{lab_str}]"
    else:
        return ""


def grid_sort(vos, label_to_extend, grid):
    def key(v):
        if label_to_extend in v:
            return grid.index(v[label_to_extend])
        else:
            return grid[0]

    return sorted(vos, key=key)
