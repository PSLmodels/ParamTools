import json

from marshmallow import fields

from paramtools.schema import Float64, Int8, Bool_, FIELD_MAP


def get_type(data):
    """
    would be used if "type" is defined
    """
    numeric_types = {"int": Int8(), "bool": Bool_(), "float": Float64()}
    types = dict(FIELD_MAP, **numeric_types)
    fieldtype = types[data["type"]]
    dim = data["number_dims"]
    while dim > 0:
        fieldtype = fields.List(fieldtype)
        dim -= 1
    return fieldtype


def read_json(path):
    """
    Read JSON file shortcut
    """
    with open(path, "r") as f:
        r = json.loads(f.read())
    return r


def get_example_paths(name):
    import os

    assert name in ("taxcalc", "weather")
    current_path = os.path.abspath(os.path.dirname(__file__))
    schema_def_path = os.path.join(
        current_path, f"../examples/{name}/schema.json"
    )
    default_spec_path = os.path.join(
        current_path, f"../examples/{name}/defaults.json"
    )
    return (schema_def_path, default_spec_path)
