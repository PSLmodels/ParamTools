import os

import pytest

from marshmallow import fields, Schema

from paramtools import Parameters


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class CompatibleDataSchema(Schema):
    """
    Schema for Compatible data object
    {
        "compatible_data": {"data1": bool, "data2": bool, ...}
    }
    """

    puf = fields.Boolean()
    cps = fields.Boolean()


@pytest.fixture
def field_map():
    return {"compatible_data": fields.Nested(CompatibleDataSchema())}


@pytest.fixture
def defaults_spec_path():
    return os.path.join(CURRENT_PATH, "../../examples/taxparams/defaults.json")


@pytest.fixture
def TaxcalcParams(defaults_spec_path, field_map):
    class _TaxcalcParams(Parameters):
        defaults = defaults_spec_path
        field_map = {"compatible_data": fields.Nested(CompatibleDataSchema())}

    return _TaxcalcParams


def test_load_schema(TaxcalcParams):
    params = TaxcalcParams()
    assert params


@pytest.fixture
def demo_defaults_spec_path():
    return os.path.join(
        CURRENT_PATH, "../../examples/taxparams-demo/defaults.json"
    )


@pytest.fixture
def TaxDemoParams(demo_defaults_spec_path):
    class _TaxDemoParams(Parameters):
        defaults = demo_defaults_spec_path

    return _TaxDemoParams


def test_load_demo_schema(TaxDemoParams):
    params = TaxDemoParams()
    assert params
