import os
import json

import pytest

from marshmallow import exceptions

from paramtools import parameters

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def field_map():
    # nothing here for now
    return {}


@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, "../../examples/weather/schema.json")


@pytest.fixture
def defaults_spec_path():
    return os.path.join(CURRENT_PATH, "../../examples/weather/defaults.json")


@pytest.fixture
def WeatherParams(schema_def_path, defaults_spec_path):
    class _WeatherParams(parameters.Parameters):
        schema = schema_def_path
        defaults = defaults_spec_path

    return _WeatherParams


def test_load_schema(WeatherParams):
    params = WeatherParams()


def test_get_all_parameters(WeatherParams, defaults_spec_path):
    wp = WeatherParams()
    params = wp.get_all()
    assert set(params.keys()) == set(
        ["average_high_temperature", "average_precipitation"]
    )
    with open(defaults_spec_path) as f:
        exp = json.loads(f.read())
    assert (
        params["average_high_temperature"]
        == exp["average_high_temperature"]["value"]
    )
    assert (
        params["average_precipitation"]
        == exp["average_precipitation"]["value"]
    )

    exp = {
        "average_high_temperature": [
            {
                "value": 59,
                "month": "November",
                "city": "Washington, D.C.",
                "dayofmonth": 1,
            },
            {
                "value": 64,
                "month": "November",
                "city": "Atlanta, GA",
                "dayofmonth": 1,
            },
        ],
        "average_precipitation": [
            {"value": 3.0, "month": "November", "city": "Washington, D.C."},
            {"value": 3.6, "month": "November", "city": "Atlanta, GA"},
        ],
    }

    assert wp.get_all(month="November") == exp


def test_failed_udpate(WeatherParams):
    adjustment = {
        "average_high_temperature": [
            {
                "city": "Washington, D.C.",
                "month": "November",
                "dayofmonth": 1,
                "value": 60,
            },
            {
                "city": "Atlanta, GA",
                "month": "November",
                "dayofmonth": 2,
                "value": 63,
            },
        ]
    }
    params = WeatherParams()
    with pytest.raises(parameters.ParameterUpdateException):
        params.adjust(adjustment)


def test_failed_get(WeatherParams):
    params = WeatherParams()
    with pytest.raises(parameters.ParameterGetException):
        params.get("average_precipitation", notallowed=1)


def test_doc_example(schema_def_path, defaults_spec_path):
    from paramtools.parameters import Parameters
    from paramtools.utils import get_example_paths

    adjustment = {
        "average_high_temperature": [
            {
                "city": "Washington, D.C.",
                "month": "November",
                "dayofmonth": 1,
                "value": 60,
            },
            {
                "city": "Atlanta, GA",
                "month": "November",
                "dayofmonth": 1,
                "value": 63,
            },
        ]
    }
    # project_schema, baseline_parameters = get_example_paths('weather')
    class WeatherParams(parameters.Parameters):
        schema = schema_def_path
        defaults = defaults_spec_path

    params = WeatherParams()
    print(params.get("average_high_temperature", month="November"))

    params.adjust(adjustment)
    print(params.get("average_high_temperature", month="November"))

    adjustment["average_high_temperature"][0]["value"] = "HOT"

    # raises error:
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.adjust(adjustment)

    # raises error:
    adjustment["average_high_temperature"][0]["value"] = 2000
    adjustment["average_high_temperature"][1]["value"] = 3000

    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.adjust(adjustment)
    print(excinfo)
