import os
import json

import pytest

from paramtools import ValidationError, SparseValueObjectsException

from paramtools import Parameters

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def schema_def_path():
    return os.path.join(CURRENT_PATH, "schema.json")


@pytest.fixture
def defaults_spec_path():
    return os.path.join(CURRENT_PATH, "defaults.json")


@pytest.fixture
def TestParams(schema_def_path, defaults_spec_path):
    class _TestParams(Parameters):
        schema = schema_def_path
        defaults = defaults_spec_path

    return _TestParams


def test_load_schema(TestParams):
    params = TestParams()
    assert params


def test_specification_and_get(TestParams, defaults_spec_path):
    params = TestParams()
    spec1 = params.specification()

    with open(defaults_spec_path) as f:
        exp = json.loads(f.read())

    assert set(spec1.keys()) == set(exp.keys())

    assert spec1["min_int_param"] == exp["min_int_param"]["value"]

    exp = {
        "min_int_param": [{"dim0": "one", "dim1": 2, "value": 2}],
        "max_int_param": [{"dim0": "one", "dim1": 2, "value": 4}],
    }
    spec2 = params.specification(dim0="one")
    # check that specification method got only the value item with dim0="one"
    assert spec2["min_int_param"] == exp["min_int_param"]
    assert spec2["max_int_param"] == exp["max_int_param"]

    # check that get method got only value item with dim0="one"
    assert params.get("min_int_param", dim0="one") == exp["min_int_param"]
    assert params.get("max_int_param", dim0="one") == exp["max_int_param"]

    # check that specification method gets other data, not containing a dim0
    # dimension.
    for param, data in spec1.items():
        if all("dim0" not in val_item for val_item in data):
            assert spec2[param] == data

    # check that get method throws a KeyError when the dimension is wrong
    with pytest.raises(KeyError):
        params.get("max_int_param", notadimension="heyo")


def test_adjust_int_param(TestParams):
    params = TestParams()

    adjustment = {"min_int_param": [{"dim0": "one", "dim1": 2, "value": 3}]}
    params.adjust(adjustment)
    assert (
        params.get("min_int_param", dim0="one", dim1=2)
        == adjustment["min_int_param"]
    )


def test_simultaneous_adjust(TestParams):
    """
    Adjust min_int_param above original max_int_param value at same time as
    max_int_param value is adjusted up. This tests that the new param is
    compared against the adjusted reference param if the reference param is
    specified.
    """
    params = TestParams()
    adjustment = {
        "min_int_param": [{"dim0": "zero", "dim1": 1, "value": 4}],
        "max_int_param": [{"dim0": "zero", "dim1": 1, "value": 5}],
    }
    params.adjust(adjustment)
    assert (
        params.get("min_int_param", dim0="zero", dim1=1)
        == adjustment["min_int_param"]
    )
    assert (
        params.get("max_int_param", dim0="zero", dim1=1)
        == adjustment["max_int_param"]
    )


def test_errors_choice_param(TestParams):
    params = TestParams()
    adjustment = {"str_choice_param": [{"value": "not a valid choice"}]}
    with pytest.raises(ValidationError) as excinfo:
        params.adjust(adjustment)
    msg = [
        'str_choice_param "not a valid choice" must be in list of choices value0, '
        "value1 for dimensions ."
    ]
    assert excinfo.value.messages["str_choice_param"][0] == msg

    params = TestParams()
    adjustment = {"str_choice_param": [{"value": 4}]}
    params = TestParams()
    with pytest.raises(ValidationError) as excinfo:
        params.adjust(adjustment)
    msg = ["Not a valid string: 4."]
    assert excinfo.value.args[0]["str_choice_param"] == msg

    params = TestParams()
    params.adjust(adjustment, raise_errors=False)
    msg = ["Not a valid string: 4."]
    assert params.errors["str_choice_param"] == msg

    params = TestParams()
    with pytest.raises(ValidationError) as excinfo:
        params.adjust(adjustment)
    msg = ["Not a valid string: 4."]
    assert excinfo.value.args[0]["str_choice_param"] == msg

    params = TestParams()
    params.adjust(adjustment, raise_errors=False)
    params.errors["str_choice_param"] == ["Not a valid string: 4"]
    # params.errors["str_choice_param"] == ["Not a valid string: 4"]


def test_errors_default_reference_param(TestParams):
    params = TestParams()
    # value under the default.
    curr = params.get("int_default_param")[0]["value"]
    adjustment = {"int_default_param": [{"value": curr - 1}]}
    params.adjust(adjustment, raise_errors=False)
    exp = [
        f"int_default_param {curr-1} must be greater than 2 for dimensions "
    ]
    assert params.errors["int_default_param"] == exp


def test_errors_int_param(TestParams):
    params = TestParams()
    adjustment = {
        "min_int_param": [{"dim0": "zero", "dim1": 1, "value": "not a number"}]
    }

    params.adjust(adjustment, raise_errors=False)
    exp = {"min_int_param": ["Not a valid number: not a number."]}
    assert params.errors == exp


def test_errors_multiple_params(TestParams):
    params = TestParams()
    adjustment = {
        "min_int_param": [
            {"dim0": "zero", "dim1": 1, "value": "not a number"},
            {"dim0": "one", "dim1": 2, "value": "still not a number"},
        ],
        "date_param": [{"dim0": "zero", "dim1": 1, "value": "not a date"}],
    }

    params.adjust(adjustment, raise_errors=False)
    exp = {
        "min_int_param": [
            "Not a valid number: not a number.",
            "Not a valid number: still not a number.",
        ],
        "date_param": ["Not a valid date: not a date."],
    }
    assert params.errors == exp


def test_to_array(TestParams):
    params = TestParams()
    res = params.to_array("int_dense_array_param")

    exp = [
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
            [13, 14, 15],
            [16, 17, 18],
        ],
        [
            [19, 20, 21],
            [22, 23, 24],
            [25, 26, 27],
            [28, 29, 30],
            [31, 32, 33],
            [34, 35, 36],
        ],
    ]

    assert res.tolist() == exp

    exp = params.int_dense_array_param["value"]
    assert params.from_array("int_dense_array_param", res) == exp

    params.int_dense_array_param["value"].pop(0)

    with pytest.raises(SparseValueObjectsException):
        params.to_array("int_dense_array_param")


def test_list_type_errors(TestParams):
    params = TestParams()

    adj = {
        "float_list_param": [
            {"value": ["abc", 0, "def", 1], "dim0": "zero", "dim1": 1},
            {"value": [-1, "ijk"], "dim0": "one", "dim1": 2},
        ]
    }
    with pytest.raises(ValidationError) as excinfo:
        params.adjust(adj)
    exp_user_message = {
        "float_list_param": [
            "Not a valid number: abc.",
            "Not a valid number: def.",
            "Not a valid number: ijk.",
        ]
    }
    assert excinfo.value.args[0] == exp_user_message

    exp_internal_message = {
        "float_list_param": [
            ["Not a valid number: abc.", "Not a valid number: def."],
            ["Not a valid number: ijk."],
        ]
    }
    assert excinfo.value.messages == exp_internal_message

    exp_dims = {
        "float_list_param": [
            {"dim0": "zero", "dim1": 1},
            {"dim0": "one", "dim1": 2},
        ]
    }
    assert excinfo.value.dims == exp_dims


def test_errors(TestParams):
    params = TestParams()
    adj = {"min_int_param": [{"value": "abc"}]}
    with pytest.raises(ValidationError) as excinfo:
        params.adjust(adj)

    exp_user_message = {"min_int_param": ["Not a valid number: abc."]}
    assert excinfo.value.args[0] == exp_user_message

    exp_internal_message = {"min_int_param": [["Not a valid number: abc."]]}
    assert excinfo.value.messages == exp_internal_message

    exp_dims = {"min_int_param": [{}]}
    assert excinfo.value.dims == exp_dims


def test_range_validation_on_list_param(TestParams):
    params = TestParams()
    adj = {"float_list_param": [{"value": [-1, 1], "dim0": "zero", "dim1": 1}]}
    params.adjust(adj, raise_errors=False)
    exp = [
        "float_list_param [-1.0, 1.0] must be greater than 0 for dimensions dim0=zero , dim1=1"
    ]

    assert params.errors["float_list_param"] == exp


def test_errors_attribute(TestParams):
    params = TestParams()
    assert params.errors == {}
