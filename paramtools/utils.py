import json

from marshmallow import fields

from paramtools.schema import Float64, Int8, Bool_

# def get_type(data, max_dim=2):
#     """
#     Use "boolean_value" and "integer_value" to figure out what type the value
#     should be. Use the shape of the data in "value" to figure out what
#     shape the parameter should have.
#     """
#     if data['boolean_value']:
#         fieldtype = Bool_()
#     elif data['integer_value']:
#         fieldtype = Int8()
#     else:
#         fieldtype = Float64()
#     if isinstance(data['value'], list):
#         if isinstance(data['value'][0], list):
#             dim = 2
#         else:
#             dim = 1
#     else:
#         dim = 0
#     while dim > 0:
#         fieldtype = fields.List(fieldtype)
#         dim -= 1
#     return fieldtype


def get_type(data):
    """
    would be used if "type" is defined
    """
    types = {"int": Int8(), "bool": Bool_(), "float": Float64()}
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
        current_path, f"../examples/{name}/baseschema.json"
    )
    base_spec_path = os.path.join(
        current_path, f"../examples/{name}/baseline.json"
    )
    return (schema_def_path, base_spec_path)
