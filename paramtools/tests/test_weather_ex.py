import os

import pytest

from marshmallow import exceptions, fields, Schema

from paramtools.build_schema import SchemaBuilder

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def field_map():
    # nothing here for now
    return {}


@pytest.fixture
def revision():
    return {
        "average_high_temperature": [
            {"city": "Washington, D.C.",
            "month": "November",
            "dayofmonth": 1,
            "value": 60},
            {"city": "Washington, D.C.",
            "month": "November",
            "dayofmonth": 2,
            "value": 63},
        ],
        "average_precipitation": [
            {"city": "Atlanta, GA",
             "month": "November",
             "value":1}
        ]
    }



@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, "../../examples/weather/baseschema.json")


@pytest.fixture
def base_spec_path():
    return os.path.join(CURRENT_PATH, "../../examples/weather/baseline.json")


def test_load_schema(revision, schema_def_path, base_spec_path, field_map):
    sb = SchemaBuilder(schema_def_path, base_spec_path, field_map)
    sb.build_schemas()

    with open(base_spec_path, "r") as f:
        res = sb.param_schema.loads(f.read())
    res = sb.load_params(revision)


def test_doc_example(schema_def_path, base_spec_path):
    from paramtools.build_schema import SchemaBuilder
    from paramtools.utils import get_example_paths

    revision = {
        "average_high_temperature": [
            {"city": "Washington, D.C.",
            "month": "November",
            "dayofmonth": 1,
            "value": 60},
            {"city": "Washington, D.C.",
            "month": "November",
            "dayofmonth": 2,
            "value": 63}
        ]
    }
    schema_def_path, base_spec_path = get_example_paths('weather')
    sb = SchemaBuilder(schema_def_path, base_spec_path)
    sb.build_schemas()
    deserialized_revision = sb.load_params(revision)
    print(deserialized_revision)

    revision["average_high_temperature"][0]["value"] = "HOT"

    # raises error:
    with pytest.raises(exceptions.ValidationError) as excinfo:
        deserialized_revision = sb.load_params(revision)