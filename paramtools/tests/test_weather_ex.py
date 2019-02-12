import os
import json

import pytest

from paramtools import Parameters
from paramtools import ValidationError, ParameterUpdateException

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
    class _WeatherParams(Parameters):
        schema = schema_def_path
        defaults = defaults_spec_path

    return _WeatherParams


def test_load_schema(WeatherParams):
    params = WeatherParams()


def test_specification(WeatherParams, defaults_spec_path):
    wp = WeatherParams()
    spec = wp.specification()
    assert set(spec.keys()) == set(
        ["average_high_temperature", "average_precipitation"]
    )
    with open(defaults_spec_path) as f:
        exp = json.loads(f.read())
    assert (
        spec["average_high_temperature"]
        == exp["average_high_temperature"]["value"]
    )
    assert (
        spec["average_precipitation"] == exp["average_precipitation"]["value"]
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

    assert wp.specification(month="November") == exp


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
    with pytest.raises(ParameterUpdateException):
        params.adjust(adjustment)

    def test_doc_example(schema_def_path, defaults_spec_path):
        from paramtools import Parameters
        from paramtools import get_example_paths

        # schema, defaults = get_example_paths('weather')

        class WeatherParams(Parameters):
            schema = schema_def_path
            defaults = defaults_spec_path

        params = WeatherParams()
        params.average_precipitation
        params.set_state(month="November")
        params.set_state(month="November")
        params.state

        params.average_precipitation
        adjustment = {
            "average_precipitation": [
                {"city": "Washington, D.C.", "month": "November", "value": 10},
                {"city": "Atlanta, GA", "month": "November", "value": 15},
            ]
        }

        params.adjust(adjustment)

        # check to make sure the values were updated:
        params.average_precipitation
        adjustment["average_precipitation"][0]["value"] = "rainy"
        # ==> raises error
        params.adjust(adjustment)
        adjustment["average_precipitation"][0]["value"] = "rainy"
        # ==> raises error
        params.adjust(adjustment, raise_errors=False)

        params.errors
        adjustment["average_precipitation"][0]["value"] = 1000
        adjustment["average_precipitation"][1]["value"] = 2000

        params.adjust(adjustment, raise_errors=False)

        params.errors
        arr = params.to_array("average_precipitation")
        arr
        vi_list = params.from_array("average_precipitation", arr)
        vi_list
