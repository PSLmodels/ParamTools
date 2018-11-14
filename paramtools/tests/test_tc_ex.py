import os

import pytest

from marshmallow import exceptions, fields, Schema

from paramtools.parameters import Parameters

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
def revision():
    return {
        "_cpi_offset": [
            {"year": "2015", "value": 0.0025},
            {"year": "2017", "value": 0.0025},
        ],
        "_STD": [{"year": 2018, "MARS": "separate", "value": 12001.00}],
        "_II_em": [{"year": 2020, "value": 5000}],
        "_II_brk1": [{"year": 2016, "MARS": "single", "value": 37649.00}],
    }


@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, "../../examples/taxcalc/baseschema.json")


@pytest.fixture
def base_spec_path():
    return os.path.join(CURRENT_PATH, "../../examples/taxcalc/baseline.json")


@pytest.fixture
def TaxcalcParams(schema_def_path, base_spec_path, field_map):
    class _TaxcalcParams(Parameters):
        project_schema = schema_def_path
        baseline_parameters = base_spec_path
        field_map = {"compatible_data": fields.Nested(CompatibleDataSchema())}

    return _TaxcalcParams


def test_load_schema(revision, TaxcalcParams):
    params = TaxcalcParams()


def test_schema_with_errors(revision, TaxcalcParams):
    params = TaxcalcParams()

    a = revision.copy()
    a["_cpi_offset"][0]["year"] = 2000
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(a)

    b = revision.copy()
    b["_STD"][0]["MARS"] = "notastatus"
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(b)

    c = revision.copy()
    c["_II_brk1"][0]["value"] = "abc"
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(c)

    c = revision.copy()
    c["_II_em"][0]["value"] = [4000.0]
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(c)


def test_range_validation(TaxcalcParams):
    revision = {"_II_em": [{"year": 2020, "value": 5000}]}
    params = TaxcalcParams()
    # parse baseline parameters to specified formats and store in
    # validator_schema context
    params.revise(revision)


def test_range_validation_fail(TaxcalcParams):
    revision = {"_II_em": [{"year": 2020, "value": -1}]}
    params = TaxcalcParams()
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(revision)
    print(excinfo)


def test_range_validation_on_named_variable(TaxcalcParams):
    revision = {
        "_II_brk1": [{"year": 2016, "MARS": "single", "value": 37649.00}]
    }
    params = TaxcalcParams()
    params.revise(revision)


def test_range_validation_on_named_variable_fails(TaxcalcParams):
    revision = {
        "_II_brk1": [{"year": 2016, "MARS": "single", "value": 37651.00}]
    }
    params = TaxcalcParams()
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(revision)
    print(excinfo)


def test_range_validation_on_default_variable(TaxcalcParams):
    revision = {
        "_STD": [{"year": 2018, "MARS": "separate", "value": 12001.00}]
    }
    params = TaxcalcParams()
    params.revise(revision)


def test_range_validation_on_default_variable_fails(TaxcalcParams):
    revision = {
        "_STD": [{"year": 2018, "MARS": "separate", "value": 11999.00}]
    }
    params = TaxcalcParams()
    with pytest.raises(exceptions.ValidationError) as excinfo:
        params.revise(revision)
    print(excinfo)


# def test_doc_example(TaxcalcParams):
#
#     revision = """{
#         "_cpi_offset": [{"year": "2015", "value": 0.0025},
#                         {"year": "2017", "value": 0.0025}],
#         "_STD": [{"year": 2018, "MARS": "separate", "value": 12001.00}],
#         "_II_em": [{"year": 2020, "value": 5000}],
#         "_II_brk1": [{"year": 2016, "MARS": "single", "value": 37649.00}]
#     }"""

#     params = TaxcalcParams(schema_def_path, base_spec_path, field_map)
#     deserialized_revision = params.revise(revision)
