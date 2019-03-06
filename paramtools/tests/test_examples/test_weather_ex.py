import os

import pytest

from paramtools import Parameters

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
    assert params
