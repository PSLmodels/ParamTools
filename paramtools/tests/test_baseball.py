import os

import pytest

from marshmallow import ValidationError

from paramtools import parameters

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def field_map():
    # nothing here for now
    return {}


@pytest.fixture
def revision():
    return {
        "pitcher": [{"value": "Stephen Strasburg"}],
        "batter": [{"value": "Aaron Judge"}],
        "start_date": [{"value": "2018-04-10"}],
        "end_date": [{"value": "2018-05-01"}],
    }


@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, "../../examples/baseball/schema.json")


@pytest.fixture
def base_spec_path():
    return os.path.join(CURRENT_PATH, "../../examples/baseball/baseline.json")


@pytest.fixture
def BaseballParams(schema_def_path, base_spec_path):
    class _BaseballParams(parameters.Parameters):
        project_schema = schema_def_path
        baseline_parameters = base_spec_path

    return _BaseballParams


def test_load_schema(BaseballParams):
    params = BaseballParams()
    assert params


def test_revise_schema(BaseballParams, revision):
    params = BaseballParams()
    params.revise(revision)
    assert params.get("pitcher") == revision["pitcher"]

    revision["start_date"] = [{"value": "2007-01-01"}]
    params = BaseballParams()
    with pytest.raises(ValidationError):
        params.revise(revision)
