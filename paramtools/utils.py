import json
import re
import os
from collections import OrderedDict
from typing import Optional, List, Dict, Any

import fsspec
from fsspec.registry import known_implementations
import marshmallow as ma

from paramtools.typing import ValueObject, FileDictStringLike


def _is_url(maybe_url):
    """
    Determine whether string is a URL or not using marshmallow and the URL
    schemes available through fsspec.
    """
    schemes = (
        set(["http"])
        | known_implementations.keys()
        | set(list(fsspec.registry))
    )
    try:
        ma.validate.URL(schemes=schemes, require_tld=False)(maybe_url)
        return True
    except ma.exceptions.ValidationError:
        return False


def _read(
    params_or_path: FileDictStringLike,
    storage_options: Optional[Dict[str, Any]] = None,
):
    """
    Read files of the form:
    - Local file path.
    - Any URL readable by fsspec. For example:
      - s3: s3://paramtools-test/defaults.json
      - gcs: gs://paramtools-dev/defaults.json
      - http: https://somedomain.com/defaults.json
      - github: github://PSLmodels:ParamTools@master/paramtools/tests/defaults.json

    """
    if isinstance(params_or_path, str) and os.path.exists(params_or_path):
        with open(params_or_path, "r") as f:
            return f.read()

    if isinstance(params_or_path, str) and _is_url(params_or_path):
        with fsspec.open(params_or_path, "r", **(storage_options or {})) as f:
            return f.read()

    if isinstance(params_or_path, str):
        return params_or_path

    if isinstance(params_or_path, dict):
        return params_or_path

    else:
        raise TypeError(
            f"Unable to read data of type: {type(params_or_path)}\n"
            "           Data must be a File Path, URL, String, or Dict."
        )


def remove_comments(string):
    """
    Remove single and multiline comments from JSON.

    StackOverflow magic:
    https://stackoverflow.com/a/18381470/9100772
    """
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "\n"  # preserve line numbers
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)


def read_json(
    params_or_path: FileDictStringLike,
    storage_options: Optional[Dict[str, Any]] = None,
):
    """
    Read JSON data of the form:
    - Dict.
    - JSON string.
    - Local file path.
    - Any URL readable by fsspec. For example:
      - s3: s3://paramtools-test/defaults.json
      - gcs: gs://paramtools-dev/defaults.json
      - http: https://somedomain.com/defaults.json
      - github: github://PSLmodels:ParamTools@master/paramtools/tests/defaults.json

    """
    res = _read(params_or_path, storage_options)
    if isinstance(res, str):
        try:
            res = remove_comments(res)
            return json.loads(res, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError as je:
            if len(res) > 100:
                res = res[:100] + "..." + res[-10:]
            raise ValueError(f"Unable to decode JSON string: {res}") from je

    if isinstance(res, dict):
        return res

    # Error should be thrown in `_read`
    raise TypeError(f"Unknown type: {type(res)}")


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
    used = set(k for k in value_items[0] if k not in ("value", "_auto"))
    for vo in value_items:
        if used != set(k for k in vo if k not in ("value", "_auto")):
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
    return tuple(
        (label, value)
        for label, value in sorted(vo.items())
        if label not in ("_auto",)
    )


def filter_labels(vo: ValueObject, drop=None, keep=None) -> ValueObject:
    """
    Filter a value objects labels by keeping labels
    in keep if specified and dropping labels that are in drop.
    """
    drop = drop or ()
    keep = keep or ()
    return {
        lab: lv
        for lab, lv in vo.items()
        if (lab not in drop) and (not keep or lab in keep)
    }


def make_label_str(vo: ValueObject) -> str:
    """
    Create string from labels. This is used to create error messages.
    """
    lab_str = ", ".join(
        [
            f"{lab}={vo[lab]}"
            for lab in sorted(vo)
            if lab not in ("value", "_auto")
        ]
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
