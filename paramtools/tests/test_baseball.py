import os

import pytest

from paramtools import ValidationError
from paramtools import parameters

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def field_map():
    # nothing here for now
    return {}


@pytest.fixture
def adjustment():
    return {
        "pitcher": [{"value": "Julio Teheran"}],
        "batter": [{"value": "Bryce Harper"}],
        "start_date": [{"value": "2018-04-10"}],
        "end_date": [{"value": "2018-05-01"}],
    }


@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, "../examples/baseball/schema.json")


@pytest.fixture
def defaults_spec_path():
    return os.path.join(CURRENT_PATH, "../examples/baseball/defaults.json")


@pytest.fixture
def BaseballParams(schema_def_path, defaults_spec_path):
    class _BaseballParams(parameters.Parameters):
        schema = schema_def_path
        defaults = defaults_spec_path

    return _BaseballParams


def test_load_schema(BaseballParams):
    params = BaseballParams()
    assert params


def test_adjust_schema(BaseballParams, adjustment):
    params = BaseballParams()
    params.adjust(adjustment)
    assert params.pitcher == adjustment["pitcher"]

    a1 = dict(adjustment, **{"start_date": [{"value": "2007-01-01"}]})
    params = BaseballParams()
    with pytest.raises(ValidationError):
        params.adjust(a1)

    a2 = dict(adjustment, **{"pitcher": [{"value": "not a pitcher"}]})
    params = BaseballParams()
    with pytest.raises(ValidationError):
        params.adjust(a2)
