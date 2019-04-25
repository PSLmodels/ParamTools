import os
import json
import datetime

import pytest

from paramtools import (
    ValidationError,
    SparseValueObjectsException,
    InconsistentLabelsException,
    collision_list,
    ParameterNameCollisionException,
)

from paramtools import Parameters

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def defaults_spec_path():
    return os.path.join(CURRENT_PATH, "defaults.json")


@pytest.fixture
def array_first_defaults(defaults_spec_path):
    with open(defaults_spec_path) as f:
        r = json.loads(f.read())
    r.pop("float_list_param")
    r.pop("simple_int_list_param")
    return r


@pytest.fixture
def TestParams(defaults_spec_path):
    class _TestParams(Parameters):
        defaults = defaults_spec_path

    return _TestParams


@pytest.fixture(scope="function")
def af_params(array_first_defaults):
    class AFParams(Parameters):
        defaults = array_first_defaults

    _af_params = AFParams(
        initial_state={"label0": "zero", "label1": 1}, array_first=True
    )
    return _af_params


def test_init(TestParams):
    params = TestParams()
    assert params
    assert params._data
    for param in params._data:
        assert getattr(params, param)
    assert params.label_grid
    assert params.label_grid == params._stateless_label_grid


class TestEmptySchema:
    def test_empty_schema(self):
        class Params(Parameters):
            array_first = True
            defaults = {
                "hello_world": {
                    "title": "Hello, World!",
                    "description": "Simplest config possible.",
                    "type": "str",
                    "value": "hello world",
                }
            }

        params = Params()
        assert params.hello_world == "hello world"
        assert params.label_grid == {}

    def test_schema_just_labels(self):
        class Params(Parameters):
            array_first = True
            defaults = {
                "schema": {
                    "labels": {
                        "somelabel": {
                            "type": "int",
                            "validators": {"range": {"min": 0, "max": 2}},
                        }
                    }
                },
                "hello_world": {
                    "title": "Hello, World!",
                    "description": "Simplest config possible.",
                    "type": "str",
                    "value": "hello world",
                },
            }

        params = Params()
        assert params.hello_world == "hello world"
        assert params.label_grid == {"somelabel": [0, 1, 2]}

    def test_schema_just_additional_members(self):
        class Params(Parameters):
            array_first = True
            defaults = {
                "schema": {
                    "additional_members": {"additional": {"type": "str"}}
                },
                "hello_world": {
                    "title": "Hello, World!",
                    "description": "Simplest config possible.",
                    "additional": "I'm extra",
                    "type": "str",
                    "value": "hello world",
                },
            }

        params = Params()
        assert params.hello_world == "hello world"
        assert params.label_grid == {}


class TestAccess:
    def test_specification(self, TestParams, defaults_spec_path):
        params = TestParams()
        spec1 = params.specification()

        with open(defaults_spec_path) as f:
            exp = json.loads(f.read())
        exp.pop("schema")

        assert set(spec1.keys()) == set(exp.keys())

        assert spec1["min_int_param"] == exp["min_int_param"]["value"]

        exp = {
            "min_int_param": [{"label0": "one", "label1": 2, "value": 2}],
            "max_int_param": [{"label0": "one", "label1": 2, "value": 4}],
        }
        spec2 = params.specification(label0="one")
        # check that specification method got only the value item with label0="one"
        assert spec2["min_int_param"] == exp["min_int_param"]
        assert spec2["max_int_param"] == exp["max_int_param"]

        # check that get method got only value item with label0="one"
        params.set_state(label0="one")
        assert params.min_int_param == exp["min_int_param"]
        assert params.max_int_param == exp["max_int_param"]

        # check that specification method gets other data, not containing a label0
        # label.
        for param, data in spec1.items():
            if all("label0" not in val_item for val_item in data):
                assert spec2[param] == data

        params._data["str_choice_param"]["value"] = []
        assert "str_choice_param" not in params.specification()
        assert "str_choice_param" in params.specification(include_empty=True)


class TestAdjust:
    def test_adjust_int_param(self, TestParams):
        params = TestParams()
        params.set_state(label0="one", label1=2)

        adjustment = {
            "min_int_param": [{"label0": "one", "label1": 2, "value": 3}]
        }
        params.adjust(adjustment)
        assert params.min_int_param == adjustment["min_int_param"]

    def test_simultaneous_adjust(self, TestParams):
        """
        Adjust min_int_param above original max_int_param value at same time as
        max_int_param value is adjusted up. This tests that the new param is
        compared against the adjusted reference param if the reference param is
        specified.
        """
        params = TestParams()
        params.set_state(label0="zero", label1=1)
        adjustment = {
            "min_int_param": [{"label0": "zero", "label1": 1, "value": 4}],
            "max_int_param": [{"label0": "zero", "label1": 1, "value": 5}],
        }
        params.adjust(adjustment)
        assert params.min_int_param == adjustment["min_int_param"]
        assert params.max_int_param == adjustment["max_int_param"]

    def test_adjust_many_labels(self, TestParams):
        """
        Adjust min_int_param above original max_int_param value at same time as
        max_int_param value is adjusted up. This tests that the new param is
        compared against the adjusted reference param if the reference param is
        specified.
        """
        params = TestParams()
        params.set_state(label0="zero", label1=1)
        adjustment = {
            "min_int_param": [{"label0": "one", "label1": 2, "value": 2}],
            "int_default_param": 5,
            "date_param": [
                {"label0": "zero", "label1": 1, "value": "2018-01-17"}
            ],
        }
        params.adjust(adjustment)
        # min_int_param is adjusted in the _data attribute but the instance
        # attribute min_int_param is not.
        spec = params.specification(use_state=False, label0="one", label1=2)
        assert spec["min_int_param"] == adjustment["min_int_param"]
        assert params.min_int_param == [
            {"label0": "zero", "label1": 1, "value": 1}
        ]

        assert params.int_default_param == [
            {"value": adjustment["int_default_param"]}
        ]
        assert params.date_param == [
            {
                "value": datetime.date(2018, 1, 17),
                "label1": 1,
                "label0": "zero",
            }
        ]

    def test_adjust_none_basic(self, TestParams):
        params = TestParams()
        adj = {
            "min_int_param": [{"label0": "one", "label1": 2, "value": None}],
            "str_choice_param": [{"value": None}],
        }
        params.adjust(adj)

        assert len(params.min_int_param) == 1
        assert len(params.str_choice_param) == 0

    def test_adjust_none_many_values(self, TestParams):
        params = TestParams()
        adj = {"int_dense_array_param": [{"value": None}]}
        params.adjust(adj)
        assert len(params._data["int_dense_array_param"]["value"]) == 0
        assert len(params.int_dense_array_param) == 0

        params = TestParams()
        adj = {"int_dense_array_param": [{"label0": "zero", "value": None}]}
        params.adjust(adj)
        assert len(params._data["int_dense_array_param"]["value"]) == 18
        assert len(params.int_dense_array_param) == 18
        assert (
            len(
                params.specification(
                    use_state=False, include_empty=True, label0="zero"
                )["int_dense_array_param"]
            )
            == 0
        )
        assert (
            len(
                params.specification(
                    use_state=False, include_empty=True, label0="one"
                )["int_dense_array_param"]
            )
            == 18
        )


class TestErrors:
    def test_errors_attribute(self, TestParams):
        params = TestParams()
        assert params.errors == {}

    def test_errors(self, TestParams):
        params = TestParams()
        adj = {"min_int_param": [{"value": "abc"}]}
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adj)

        exp_user_message = {"min_int_param": ["Not a valid number: abc."]}
        assert excinfo.value.args[0] == exp_user_message

        exp_internal_message = {
            "min_int_param": [["Not a valid number: abc."]]
        }
        assert excinfo.value.messages == exp_internal_message

        exp_labels = {"min_int_param": [{}]}
        assert excinfo.value.labels == exp_labels

        params = TestParams()
        adj = {"min_int_param": "abc"}
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adj)

    def test_errors_choice_param(self, TestParams):
        params = TestParams()
        adjustment = {"str_choice_param": [{"value": "not a valid choice"}]}
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adjustment)
        msg = [
            'str_choice_param "not a valid choice" must be in list of choices value0, '
            "value1."
        ]
        assert excinfo.value.messages["str_choice_param"][0] == msg

        params = TestParams()
        adjustment = {"str_choice_param": [{"value": 4}]}
        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adjustment)
        msg = ["Not a valid string."]
        assert excinfo.value.args[0]["str_choice_param"] == msg

        params = TestParams()
        params.adjust(adjustment, raise_errors=False)
        msg = ["Not a valid string."]
        assert params.errors["str_choice_param"] == msg

        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adjustment)
        msg = ["Not a valid string."]
        assert excinfo.value.args[0]["str_choice_param"] == msg

        params = TestParams()
        params.adjust(adjustment, raise_errors=False)
        params.errors["str_choice_param"] == ["Not a valid string."]

    def test_errors_default_reference_param(self, TestParams):
        params = TestParams()
        params.set_state(label0="zero", label1=1)
        # value under the default.
        curr = params.int_default_param[0]["value"]
        adjustment = {"int_default_param": [{"value": curr - 1}]}
        params.adjust(adjustment, raise_errors=False)
        exp = [f"int_default_param {curr-1} must be greater than 2."]
        assert params.errors["int_default_param"] == exp

    def test_errors_int_param(self, TestParams):
        params = TestParams()
        adjustment = {
            "min_int_param": [
                {"label0": "zero", "label1": 1, "value": "not a number"}
            ]
        }

        params.adjust(adjustment, raise_errors=False)
        exp = {"min_int_param": ["Not a valid number: not a number."]}
        assert params.errors == exp

    def test_errors_multiple_params(self, TestParams):
        params = TestParams()
        adjustment = {
            "min_int_param": [
                {"label0": "zero", "label1": 1, "value": "not a number"},
                {"label0": "one", "label1": 2, "value": "still not a number"},
            ],
            "date_param": [
                {"label0": "zero", "label1": 1, "value": "not a date"}
            ],
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

    def test_list_type_errors(self, TestParams):
        params = TestParams()

        adj = {
            "float_list_param": [
                {"value": ["abc", 0, "def", 1], "label0": "zero", "label1": 1},
                {"value": [-1, "ijk"], "label0": "one", "label1": 2},
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

        exp_labels = {
            "float_list_param": [
                {"label0": "zero", "label1": 1},
                {"label0": "one", "label1": 2},
            ]
        }
        assert excinfo.value.labels == exp_labels

    def test_range_validation_on_list_param(self, TestParams):
        params = TestParams()
        adj = {
            "float_list_param": [
                {"value": [-1, 1], "label0": "zero", "label1": 1}
            ]
        }
        params.adjust(adj, raise_errors=False)
        exp = [
            "float_list_param [-1.0, 1.0] must be greater than 0 for labels label0=zero , label1=1."
        ]

        assert params.errors["float_list_param"] == exp


class TestArray:
    def test_to_array(self, TestParams):
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

        exp = params.int_dense_array_param
        assert params.from_array("int_dense_array_param", res) == exp

        params._data["int_dense_array_param"]["value"].pop(0)

        with pytest.raises(SparseValueObjectsException):
            params.to_array("int_dense_array_param")

    def test_from_array(self, TestParams):
        params = TestParams()
        with pytest.raises(TypeError):
            params.from_array("min_int_param")

    def test_resolve_order(self, TestParams):
        exp_label_order = ["label0", "label2"]
        exp_value_order = {"label0": ["zero", "one"], "label2": [0, 1, 2]}
        vi = [
            {"label0": "zero", "label2": 0, "value": None},
            {"label0": "zero", "label2": 1, "value": None},
            {"label0": "zero", "label2": 2, "value": None},
            {"label0": "one", "label2": 0, "value": None},
            {"label0": "one", "label2": 1, "value": None},
            {"label0": "one", "label2": 2, "value": None},
        ]

        params = TestParams()
        params.madeup = vi
        params._data["madeup"] = {"value": vi}

        assert params._resolve_order("madeup") == (
            exp_label_order,
            exp_value_order,
        )

        # test with specified state.
        exp_value_order = {"label0": ["zero", "one"], "label2": [0, 1]}
        params.set_state(label2=[0, 1])
        assert params._resolve_order("madeup") == (
            exp_label_order,
            exp_value_order,
        )

        params.madeup[0]["label1"] = 0
        with pytest.raises(InconsistentLabelsException):
            params._resolve_order("madeup")

    def test_to_array_with_state1(self, TestParams):
        params = TestParams()
        params.set_state(label0="zero")
        res = params.to_array("int_dense_array_param")

        exp = [
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
                [10, 11, 12],
                [13, 14, 15],
                [16, 17, 18],
            ]
        ]

        assert res.tolist() == exp

        exp = params.int_dense_array_param
        assert params.from_array("int_dense_array_param", res) == exp

    def test_to_array_with_state2(self, TestParams):
        params = TestParams()
        # Drop values 3 and 4 from label1
        params.set_state(label1=[0, 1, 2, 5])
        res = params.to_array("int_dense_array_param")

        # Values 3 and 4 were removed from label1.
        exp = [
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
                # [10, 11, 12],
                # [13, 14, 15],
                [16, 17, 18],
            ],
            [
                [19, 20, 21],
                [22, 23, 24],
                [25, 26, 27],
                # [28, 29, 30],
                # [31, 32, 33],
                [34, 35, 36],
            ],
        ]

        assert res.tolist() == exp

        exp = params.int_dense_array_param
        assert params.from_array("int_dense_array_param", res) == exp


class TestState:
    def test_basic_set_state(self, TestParams):
        params = TestParams()
        assert params.view_state() == {}
        params.set_state(label0="zero")
        assert params.view_state() == {"label0": "zero"}
        params.set_state(label1=0)
        assert params.view_state() == {"label0": "zero", "label1": 0}
        params.set_state(label0="one", label2=1)
        assert params.view_state() == {
            "label0": "one",
            "label1": 0,
            "label2": 1,
        }
        params.set_state(**{})
        assert params.view_state() == {
            "label0": "one",
            "label1": 0,
            "label2": 1,
        }
        params.set_state()
        assert params.view_state() == {
            "label0": "one",
            "label1": 0,
            "label2": 1,
        }
        params.set_state(label1=[1, 2, 3])
        assert params.view_state() == {
            "label0": "one",
            "label1": [1, 2, 3],
            "label2": 1,
        }

    def test_label_grid(self, TestParams):
        params = TestParams()
        exp = {
            "label0": ["zero", "one"],
            "label1": [0, 1, 2, 3, 4, 5],
            "label2": [0, 1, 2],
        }
        assert params.label_grid == exp

        params.set_state(label0="one")
        exp = {
            "label0": ["one"],
            "label1": [0, 1, 2, 3, 4, 5],
            "label2": [0, 1, 2],
        }
        assert params.label_grid == exp

        params.set_state(label0="one", label2=1)
        exp = {"label0": ["one"], "label1": [0, 1, 2, 3, 4, 5], "label2": [1]}
        assert params.label_grid == exp

        params.set_state(label1=[0, 1, 2, 5])
        exp = {"label0": ["one"], "label1": [0, 1, 2, 5], "label2": [1]}
        assert params.label_grid == {
            "label0": ["one"],
            "label1": [0, 1, 2, 5],
            "label2": [1],
        }

    def test_set_state_updates_values(self, TestParams):
        params = TestParams()
        defaultexp = [
            {"label0": "zero", "label1": 1, "value": 1},
            {"label0": "one", "label1": 2, "value": 2},
        ]
        assert params.min_int_param == defaultexp

        params.set_state(label0="zero")
        assert params.min_int_param == [
            {"label0": "zero", "label1": 1, "value": 1}
        ]

        # makes sure parameter that doesn't use label0 is unaffected
        assert params.str_choice_param == [{"value": "value0"}]

        params.clear_state()
        assert params.view_state() == {}
        assert params.min_int_param == defaultexp
        assert params.label_grid == params._stateless_label_grid

    def test_set_state_errors(self, TestParams):
        params = TestParams()
        with pytest.raises(ValidationError):
            params.set_state(label0="notalabel")

        params = TestParams()
        with pytest.raises(ValidationError):
            params.set_state(notalabel="notalabel")

    def test_state_with_list(self, TestParams):
        params = TestParams()
        params.set_state(label0="zero", label1=[0, 1])
        exp = [
            {"label0": "zero", "label1": 0, "label2": 0, "value": 1},
            {"label0": "zero", "label1": 0, "label2": 1, "value": 2},
            {"label0": "zero", "label1": 0, "label2": 2, "value": 3},
            {"label0": "zero", "label1": 1, "label2": 0, "value": 4},
            {"label0": "zero", "label1": 1, "label2": 1, "value": 5},
            {"label0": "zero", "label1": 1, "label2": 2, "value": 6},
        ]
        assert params.int_dense_array_param == exp


class TestArrayFirst:
    def test_basic(self, af_params):
        assert af_params
        assert af_params.min_int_param.tolist() == [[1]]
        assert af_params.date_max_param.tolist() == [
            [datetime.date(2018, 1, 15)]
        ]
        assert af_params.int_dense_array_param.tolist() == [[[4, 5, 6]]]
        assert af_params.str_choice_param.tolist() == "value0"

    def test_from_array(self, af_params):
        exp = [
            {"label0": "zero", "label1": 1, "label2": 0, "value": 4},
            {"label0": "zero", "label1": 1, "label2": 1, "value": 5},
            {"label0": "zero", "label1": 1, "label2": 2, "value": 6},
        ]
        assert af_params.from_array("int_dense_array_param") == exp

        assert (
            af_params.from_array(
                "int_dense_array_param", af_params.int_dense_array_param
            )
            == exp
        )


class TestCollisions:
    def test_collision_list(self):
        class CollisionParams(Parameters):
            defaults = {"schema": {"labels": {}, "additional_members": {}}}

        params = CollisionParams()

        # check to make sure that the collisionlist does not need to be updated.
        # Note: dir(obj) lists out all class or instance attributes and methods.
        assert set(collision_list) == {
            name for name in dir(params) if not name.startswith("__")
        }

    def test_collision(self):
        defaults_dict = {
            "schema": {"labels": {}, "additional_members": {}},
            "errors": {
                "title": "Collides with 'errors'",
                "description": "",
                "notes": "",
                "type": "int",
                "value": [{"value": 0}],
                "validators": {"range": {"min": 0, "max": 10}},
            },
        }

        class CollisionParams(Parameters):
            defaults = defaults_dict

        with pytest.raises(ParameterNameCollisionException) as excinfo:
            CollisionParams()

        exp_msg = (
            "The paramter name, 'errors', is already used by the "
            "Parameters object."
        )

        assert excinfo.value.args[0] == exp_msg
