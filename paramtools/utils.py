import json
import os
from collections import OrderedDict


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


def consistent_labels(value_items):
    """
    Get labels used consistently across all value objects.
    Returns None if labels are omitted or added for
    some value object(s).
    """
    used = set(k for k in value_items[0] if k != "value")
    for vo in value_items:
        if used != set(k for k in vo if k != "value"):
            return None
    return used


def ensure_value_object(vo):
    if not isinstance(vo, list) or (
        isinstance(vo, list) and not isinstance(vo[0], dict)
    ):
        vo = [{"value": vo}]
    return vo
