import os

import pytest

from marshmallow import exceptions

from paramtools import parameters

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def field_map():
    # nothing here for now
    return {}


@pytest.fixture
def revision():
    return {
        "average_high_temperature": [
            {
                "city": "Washington, D.C.",
                "month": "November",
                "dayofmonth": 1,
                "value": 60,
            },
            {
                "city": "Washington, D.C.",
                "month": "November",
                "dayofmonth": 2,
                "value": 63,
            },
        ],
        "average_precipitation": [
            {"city": "Atlanta, GA", "month": "November", "value": 1}
        ],
    }


@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, "../../examples/weather/baseschema.json")


@pytest.fixture
def base_spec_path():
    return os.path.join(CURRENT_PATH, "../../examples/weather/baseline.json")


@pytest.fixture
def WeatherParams(schema_def_path, base_spec_path):
    class _WeatherParams(parameters.Parameters):
        project_schema = schema_def_path
        baseline_parameters = base_spec_path

    return _WeatherParams


def test_load_schema(revision, WeatherParams):
    params = WeatherParams()


def test_failed_udpate(WeatherParams):
    revision = {
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
        params.revise(revision)


def test_failed_get(WeatherParams):
    params = WeatherParams()
    with pytest.raises(parameters.ParameterGetException):
        params.get("average_precipitation", notallowed=1)


def test_doc_example(schema_def_path, base_spec_path):
    from paramtools.parameters import Parameters
    from paramtools.utils import get_example_paths

    revision = {
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
        project_schema = schema_def_path
        baseline_parameters = base_spec_path

    params = WeatherParams()
    print(params.get("average_high_temperature", month="November"))

    params.revise(revision)
    print(params.get("average_high_temperature", month="November"))

    revision["average_high_temperature"][0]["value"] = "HOT"

    # raises error:
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(revision)

    # raises error:
    revision["average_high_temperature"][0]["value"] = 2000
    revision["average_high_temperature"][1]["value"] = 3000

    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(revision)
    print(excinfo)