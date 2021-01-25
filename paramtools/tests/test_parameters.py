import copy
import os
import json
import datetime
from collections import OrderedDict
from random import shuffle

import pytest
import numpy as np
import marshmallow as ma

from paramtools import (
    ParamToolsError,
    ValidationError,
    SparseValueObjectsException,
    InconsistentLabelsException,
    collision_list,
    ParameterNameCollisionException,
    register_custom_type,
    Parameters,
    Values,
    Slice,
)
from paramtools.contrib import Bool_

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def defaults_spec_path():
    return os.path.join(CURRENT_PATH, "defaults.json")


@pytest.fixture
def extend_ex_path():
    return os.path.join(CURRENT_PATH, "extend_ex.json")


@pytest.fixture
def array_first_defaults(defaults_spec_path):
    with open(defaults_spec_path) as f:
        r = json.loads(f.read())
    r.pop("float_list_param")
    r.pop("simple_int_list_param")
    r.pop("float_list_when_param")
    r.pop("when_array_param")
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


class TestSchema:
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

    def test_schema_not_dropped(self, defaults_spec_path):
        with open(defaults_spec_path, "r") as f:
            defaults_ = json.loads(f.read())

        class TestParams(Parameters):
            defaults = defaults_

        TestParams()
        assert defaults_["schema"]

    def test_schema_with_errors(self):
        class Params1(Parameters):
            array_first = True
            defaults = {
                "schema": {
                    "additional_members": {"additional": {"type": 1234}}
                }
            }

        with pytest.raises(ma.ValidationError):
            Params1()

        class Params2(Parameters):
            array_first = True
            defaults = {
                "schema": {
                    "additional_members_123": {"additional": {"type": "str"}}
                }
            }

        with pytest.raises(ma.ValidationError):
            Params2()

    def test_operators_spec(self):
        class Params1(Parameters):
            array_first = False
            defaults = {
                "schema": {
                    "labels": {
                        "mylabel": {
                            "type": "int",
                            "validators": {"range": {"min": 0, "max": 10}},
                        },
                        "somelabel": {
                            "type": "int",
                            "validators": {"range": {"min": 0, "max": 10}},
                        },
                    },
                    "operators": {
                        "array_first": False,
                        "label_to_extend": "somelabel",
                    },
                }
            }

        params = Params1(array_first=True, label_to_extend="mylabel")
        assert params.array_first
        assert params.label_to_extend == "mylabel"
        assert params.operators == {
            "array_first": True,
            "label_to_extend": "mylabel",
            "uses_extend_func": False,
        }
        assert params.dump()["schema"]["operators"] == params.operators

        Params1.array_first = True
        params = Params1()
        assert params.array_first
        assert params.label_to_extend == "somelabel"
        assert params.operators == {
            "array_first": True,
            "label_to_extend": "somelabel",
            "uses_extend_func": False,
        }
        assert params.dump()["schema"]["operators"] == params.operators

        class Params2(Parameters):
            defaults = {"schema": {"operators": {"array_first": True}}}

        params = Params2()
        assert params.array_first
        assert params.label_to_extend is None
        assert params.operators == {
            "array_first": True,
            "label_to_extend": None,
            "uses_extend_func": False,
        }
        assert params.dump()["schema"]["operators"] == params.operators

        class Params3(Parameters):
            array_first = True
            label_to_extend = "hello"
            defaults = {"schema": {"operators": {"array_first": True}}}

        params = Params3(array_first=False, label_to_extend=None)
        assert params.operators == {
            "array_first": False,
            "label_to_extend": None,
            "uses_extend_func": False,
        }
        assert params.dump()["schema"]["operators"] == params.operators

        params.array_first = True
        assert params.dump()["schema"]["operators"] == params.operators

    def test_when_schema(self):
        class Params(Parameters):
            defaults = {
                "param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "value": 0,
                    "validators": {
                        "when": {
                            "param": "default",
                            "is": {"less_than": 0, "greater_than": 1},
                            "then": {"range": {"min": 0}},
                            "otherwise": {"range": {"min": "default"}},
                        }
                    },
                }
            }

        with pytest.raises(ma.ValidationError):
            Params()

    def test_custom_fields(self):
        class Custom(ma.Schema):
            hello = ma.fields.Boolean()
            world = Bool_()  # Tests data is serialized.

        register_custom_type("custom_type", ma.fields.Nested(Custom()))

        class Params(Parameters):
            defaults = {
                "schema": {
                    "labels": {"custom_label": {"type": "custom_type"}},
                    "additional_members": {"custom": {"type": "custom_type"}},
                },
                "param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "value": [{"custom_label": {"hello": True}, "value": 0}],
                    "custom": {"hello": True, "world": True},
                },
            }

        params = Params()
        assert params
        assert params._data["param"]["custom"] == {
            "hello": True,
            "world": True,
        }
        assert params.adjust(
            {
                "param": [
                    {
                        "custom_label": {"hello": True, "world": True},
                        "value": 1,
                    }
                ]
            }
        )
        assert params.sel["param"].isel[:] == [
            {"custom_label": {"hello": True}, "value": 0},
            {"custom_label": {"hello": True, "world": True}, "value": 1},
        ]

        class BadSpec(Parameters):
            field_map = {"custom_type": ma.fields.Nested(Custom)}
            defaults = {
                "schema": {
                    "additional_members": {"custom": {"type": "custom_type"}}
                },
                "param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "value": 0,
                    "custom": {"hello": 123, "world": "whoops"},
                },
            }

        with pytest.raises(ma.ValidationError):
            BadSpec()


class TestValues:
    def test(self, TestParams, defaults_spec_path):
        params = TestParams()
        assert isinstance(params.sel["min_int_param"], Values)
        assert isinstance(params.sel["min_int_param"]["label0"], Slice)

        with pytest.raises(AttributeError):
            params["min_int_param"]


class TestAccess:
    def test_specification(self, TestParams, defaults_spec_path):
        params = TestParams()
        spec1 = params.specification()

        with open(defaults_spec_path) as f:
            exp = json.loads(f.read())
        exp.pop("schema")

        assert set(spec1.keys()) == set(exp.keys())

        assert spec1["min_int_param"] == exp["min_int_param"]["value"]

    def test_is_ordered(self, TestParams):
        params = TestParams()
        spec1 = params.specification()
        assert isinstance(spec1, OrderedDict)

        spec2 = params.specification(meta_data=True, serializable=True)
        assert isinstance(spec2, OrderedDict)

    def test_specification_query(self, TestParams):
        params = TestParams()
        spec1 = params.specification()
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

        params.delete({"str_choice_param": None})
        assert "str_choice_param" not in params.specification()
        assert "str_choice_param" in params.specification(include_empty=True)

    def test_serializable(self, TestParams, defaults_spec_path):
        params = TestParams()

        assert json.dumps(params.specification(serializable=True))
        assert json.dumps(
            params.specification(serializable=True, meta_data=True)
        )

        spec = params.specification(serializable=True)
        # Make sure "value" is removed when meta_data is False
        for value in spec.values():
            assert "value" not in value

        with open(defaults_spec_path) as f:
            exp = json.loads(f.read())
        exp.pop("schema")

        spec = params.specification(serializable=True, meta_data=True)
        assert spec == params._defaults_schema.dump(
            params._defaults_schema.load(exp)
        )

    def test_dump(self, TestParams, defaults_spec_path):
        params1 = TestParams()
        spec = params1.specification(serializable=True, meta_data=True)
        schema = params1._schema
        dumped = params1.dump()
        assert dumped == {**spec, **{"schema": schema}}

        class TestParams2(Parameters):
            defaults = dumped

        params2 = TestParams2()
        assert params2.dump() == dumped

    def test_dump_with_labels(self, TestParams, defaults_spec_path):
        params1 = TestParams()
        spec = params1.specification(
            serializable=True,
            include_empty=True,
            meta_data=True,
            label0="one",
            sort_values=True,
        )
        schema = params1._schema
        params1.set_state(label0="one")
        dumped = params1.dump(sort_values=True)
        assert dumped == {**spec, **{"schema": schema}}

        class TestParams2(Parameters):
            defaults = dumped

        params2 = TestParams2()
        params2.set_state(label0="one")
        assert params2.dump() == dumped

    def test_iterable(self, TestParams):
        params = TestParams()

        act = set([])
        for param in params:
            act.add(param)

        assert set(params._data.keys()) == act
        assert set(params._data.keys()) == set(params.keys())

        for param, data in params.items():
            np.testing.assert_equal(data, getattr(params, param))

    def test_sort_values(self, TestParams):
        """Ensure sort runs and is stable"""
        sorted_tp = TestParams()
        sorted_tp.sort_values()
        assert sorted_tp.dump(sort_values=False) == TestParams().dump(
            sort_values=False
        )

        shuffled_tp = TestParams()
        for param in shuffled_tp:
            shuffle(shuffled_tp._data[param]["value"])

        shuffled_tp.sel._cache = {}

        assert sorted_tp.dump(sort_values=False) != shuffled_tp.dump(
            sort_values=False
        )

        shuffled_tp.sort_values()
        assert sorted_tp.dump(sort_values=False) == shuffled_tp.dump(
            sort_values=False
        )
        # Test attribute is updated, too.
        for param in sorted_tp:
            assert getattr(sorted_tp, param) == getattr(shuffled_tp, param)

    def test_sort_values_no_labels(self):
        class Params(Parameters):
            defaults = {
                "test": {
                    "title": "test",
                    "description": "",
                    "type": "int",
                    "value": 2,
                }
            }

        params = Params()
        assert params.sort_values() == params._data
        assert params.sort_values({"test": params.test})
        assert params.dump()

    def test_sort_values_correctness(self):
        """Ensure sort is correct"""
        exp = [
            {"value": 1},
            {"label0": 1, "label1": "one", "value": 1},
            {"label0": 1, "label1": "two", "value": 1},
            {"label0": 2, "label1": "one", "value": 1},
            {"label0": 2, "label1": "two", "value": 1},
            {"label0": 3, "label1": "one", "value": 1},
        ]
        shuffled = copy.deepcopy(exp)
        shuffle(shuffled)

        class Params(Parameters):
            defaults = {
                "schema": {
                    "labels": {
                        "label0": {
                            "type": "int",
                            "validators": {"range": {"min": 0, "max": 3}},
                        },
                        "label1": {
                            "type": "str",
                            "validators": {
                                "choice": {"choices": ["one", "two"]}
                            },
                        },
                    }
                },
                "param": {
                    "title": "test",
                    "description": "",
                    "type": "int",
                    "value": shuffled,
                },
            }

        params = Params(sort_values=False)

        assert params.param != exp and params.param == shuffled

        params.sort_values()
        assert params.param == exp

        # test passing in a data object
        params = Params(sort_values=False)
        assert params.param != exp and params.param == shuffled

        data1 = {"param": params.param}
        params.sort_values(data1, has_meta_data=False)
        data1 = copy.deepcopy(data1)

        data2 = {"param": {"value": params.param}}
        params.sort_values(data2, has_meta_data=True)
        data2 = copy.deepcopy(data2)

        params.sort_values()
        assert data1["param"] == data2["param"]["value"] == params.param

        with pytest.raises(ParamToolsError):
            params.sort_values(has_meta_data=False)

    def test_dump_sort_values(self, TestParams):
        """Test sort_values keyword in dump()"""
        tp = TestParams()
        for param in tp:
            shuffle(tp._data[param]["value"])
        tp.sel._cache = {}

        shuffled_dump = tp.dump(sort_values=False)
        sorted_dump = tp.dump(sort_values=True)

        assert sorted_dump != shuffled_dump

        sorted_tp = TestParams()
        sorted_tp.sort_values()
        assert sorted_tp.dump(sort_values=False) == sorted_dump

        # Test that sort works when state is activated
        state_tp = TestParams()
        for param in tp:
            shuffle(state_tp._data[param]["value"])
        state_tp.set_state(label0="zero", label2=1)
        state_dump = copy.deepcopy(state_tp.dump(sort_values=False))

        class NoStateParams(Parameters):
            defaults = state_dump

        nostate_tp = NoStateParams(sort_values=False)
        assert nostate_tp.dump(sort_values=False) == state_dump
        assert not nostate_tp.view_state()
        assert state_tp.view_state()

        assert nostate_tp.dump(sort_values=True) == state_tp.dump(
            sort_values=True
        )

    def test_sort_values_w_array(self, extend_ex_path):
        """Test sort values with array first config"""

        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True

        # Test that param attributes are not updated when
        # array first is True
        params = ExtParams()
        params.extend_param = "don't update me"
        params.sort_values()
        assert params.extend_param == "don't update me"

    def test_sort_values_with_state(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = False

        params = ExtParams()
        params.set_state(d0=[6, 7, 8, 9])
        params.sort_values()
        assert params.extend_param == [
            {"d0": 6, "d1": "c1", "value": 5, "_auto": True},
            {"d0": 6, "d1": "c2", "value": 6, "_auto": True},
            {"d0": 7, "d1": "c1", "value": 7},
            {"d0": 7, "d1": "c2", "value": 8},
            {"d0": 8, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 8, "d1": "c2", "value": 8, "_auto": True},
            {"d0": 9, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 9, "d1": "c2", "value": 8, "_auto": True},
        ]


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

    def test_transaction(self, TestParams):
        """
        Use transaction manager to defer schema level validation until all adjustments
        are complete.
        """
        params = TestParams()
        params.set_state(label0="zero", label1=1)
        adjustment = {
            "min_int_param": [{"label0": "zero", "label1": 1, "value": 4}],
            "max_int_param": [{"label0": "zero", "label1": 1, "value": 5}],
        }
        with params.transaction(defer_validation=True):
            params.adjust({"min_int_param": adjustment["min_int_param"]})
            params.adjust({"max_int_param": adjustment["max_int_param"]})
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
        print(params.str_choice_param)
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

    def test_delete(self, TestParams):
        params = TestParams()
        adj = {
            "min_int_param": [{"label0": "one", "label1": 2, "value": 2}],
            "str_choice_param": None,
        }
        params.delete(adj)

        assert len(params.min_int_param) == 1
        assert len(params.str_choice_param) == 0

        params = TestParams()
        adj = {"int_dense_array_param": None}
        params.delete(adj)
        assert len(params._data["int_dense_array_param"]["value"]) == 0
        assert len(params.int_dense_array_param) == 0

        params = TestParams()
        adj = {"int_dense_array_param": [{"label0": "zero", "value": 2}]}
        params.delete(adj)
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

    def test_adjust_when_param(self, TestParams):
        params = TestParams()
        params.adjust({"when_param": 2, "str_choice_param": "value1"})
        assert params.when_param == [{"value": 2}]

        params = TestParams()
        params.adjust({"when_param": 0})
        assert params.when_param == [{"value": 0}]

    def test_adjust_when_array_param(self, TestParams):
        params = TestParams()
        params.adjust({"when_array_param": [0, 1, 0, 0]})
        assert params.when_array_param == [{"value": [0, 1, 0, 0]}]

    def test_adjust_float_list_when_param(self, TestParams):
        params = TestParams()
        params.adjust({"float_list_when_param": [0, 2.0, 2.0, 2.0]})
        assert params.float_list_when_param == [
            {"label0": "zero", "value": [0, 2.0, 2.0, 2.0]}
        ]


class TestValidationMessages:
    def test_attributes(self, TestParams):
        params = TestParams()
        assert params.errors == {}
        assert params.warnings == {}

    def test_errors(self, TestParams):
        params = TestParams()
        adj = {"min_int_param": [{"value": "abc"}]}
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adj)

        exp_user_message = {"min_int_param": ["Not a valid integer: abc."]}
        assert json.loads(excinfo.value.args[0]) == {
            "errors": exp_user_message
        }

        exp_internal_message = {
            "min_int_param": [["Not a valid integer: abc."]]
        }
        assert excinfo.value.messages["errors"] == exp_internal_message

        exp_labels = {"min_int_param": [{}]}
        assert excinfo.value.labels["errors"] == exp_labels

        params = TestParams()
        adj = {"min_int_param": "abc"}
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adj)

    def test_label_errors(self, TestParams):
        params = TestParams()

        params.adjust(
            {"min_int_param": [{"value": 2, "label1": 6}]}, raise_errors=False
        )

        assert params.errors["min_int_param"] == [
            "Input 6 must be less than 5."
        ]

        params = TestParams()

        params.adjust(
            {"min_int_param": [{"value": 2, "label1": -1}]}, raise_errors=False
        )

        assert params.errors["min_int_param"] == [
            "Input -1 must be greater than 0."
        ]

    def test_errors_choice_param(self, TestParams):
        params = TestParams()
        adjustment = {"str_choice_param": [{"value": "not a valid choice"}]}
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adjustment)
        msg = [
            'str_choice_param "not a valid choice" must be in list of choices value0, '
            "value1."
        ]
        assert (
            json.loads(excinfo.value.args[0])["errors"]["str_choice_param"]
            == msg
        )

        params = TestParams()
        adjustment = {"str_choice_param": [{"value": 4}]}
        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adjustment)
        msg = ["Not a valid string."]
        assert (
            json.loads(excinfo.value.args[0])["errors"]["str_choice_param"]
            == msg
        )

        params = TestParams()
        params.adjust(adjustment, raise_errors=False)
        msg = ["Not a valid string."]
        assert params.errors["str_choice_param"] == msg

        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust(adjustment)
        msg = ["Not a valid string."]
        assert (
            json.loads(excinfo.value.args[0])["errors"]["str_choice_param"]
            == msg
        )

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
        exp = [f"int_default_param {curr-1} < min 2 default"]
        assert params.errors["int_default_param"] == exp

    def test_errors_int_param(self, TestParams):
        params = TestParams()
        adjustment = {
            "min_int_param": [{"label0": "zero", "label1": 1, "value": 2.5}]
        }

        params.adjust(adjustment, raise_errors=False)
        exp = {"min_int_param": ["Not a valid integer: 2.5."]}
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
                "Not a valid integer: not a number.",
                "Not a valid integer: still not a number.",
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
        assert json.loads(excinfo.value.args[0]) == {
            "errors": exp_user_message
        }

        exp_internal_message = {
            "float_list_param": [
                ["Not a valid number: abc.", "Not a valid number: def."],
                ["Not a valid number: ijk."],
            ]
        }
        assert excinfo.value.messages["errors"] == exp_internal_message

        exp_labels = {
            "float_list_param": [
                {"label0": "zero", "label1": 1},
                {"label0": "one", "label1": 2},
            ]
        }
        assert excinfo.value.labels["errors"] == exp_labels

        params = TestParams()
        adjustment = {"float_param": [2.5]}

        params.adjust(adjustment, raise_errors=False)
        exp = {"float_param": ["Not a valid number: [2.5]."]}
        assert params.errors == exp

        params = TestParams()
        adjustment = {"bool_param": [False]}

        params.adjust(adjustment, raise_errors=False)
        exp = {"bool_param": ["Not a valid boolean: [False]."]}
        assert params.errors == exp

    def test_range_validation_on_list_param(self, TestParams):
        params = TestParams()
        adj = {
            "float_list_param": [
                {"value": [-1, 1], "label0": "zero", "label1": 1}
            ]
        }
        params.adjust(adj, raise_errors=False)
        exp = ["float_list_param[label0=zero, label1=1] [-1.0, 1.0] < min 0 "]

        assert params.errors["float_list_param"] == exp

    def test_warnings(self, TestParams):
        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust({"str_choice_warn_param": "not a valid choice"})

        assert params.warnings
        assert not params.errors

        msg = [
            'str_choice_warn_param "not a valid choice" must be in list of choices value0, '
            "value1."
        ]
        assert (
            json.loads(excinfo.value.args[0])["warnings"][
                "str_choice_warn_param"
            ]
            == msg
        )

        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust({"int_warn_param": -1})

        assert params.warnings
        assert not params.errors

        msg = ["int_warn_param -1 < min 0 "]
        assert (
            json.loads(excinfo.value.args[0])["warnings"]["int_warn_param"]
            == msg
        )

    def test_ignore_warnings(self, TestParams):
        params = TestParams()
        params.adjust({"int_warn_param": -2}, ignore_warnings=True)
        assert params.int_warn_param == [{"value": -2}]
        assert not params.errors
        assert not params.warnings

        with pytest.raises(ValidationError):
            params.adjust({"int_warn_param": "abc"}, ignore_warnings=True)

    def test_when_validation(self):
        class Params(Parameters):
            defaults = {
                "param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "value": 0,
                    "validators": {
                        "when": {
                            "param": "when_param",
                            "is": {"less_than": 0},
                            "then": {"range": {"min": 0}},
                            "otherwise": {
                                # only valid for ndim = 0
                                "range": {"min": "when_param"}
                            },
                        }
                    },
                },
                "when_param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "value": 2,
                },
            }

        params = Params(array_first=True)
        params.adjust({"param": 3})
        assert params.param == 3.0

        params.adjust({"when_param": -2, "param": 0})

        with pytest.raises(ValidationError) as excinfo:
            params.adjust({"when_param": -2, "param": -1})

        msg = json.loads(excinfo.value.args[0])
        assert msg["errors"]["param"] == [
            "When when_param is less than 0, param value is invalid: param -1 < min 0 "
        ]

    def test_when_validation_limitations(self):
        """
        When validation prohibits child validators from doing referential validation
        when the other parameter is an array type (number_dims > 0).
        """

        class Params(Parameters):
            defaults = {
                "param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "number_dims": 1,
                    "value": [0, 0],
                    "validators": {
                        "when": {
                            "param": "when_param",
                            "is": {"less_than": 0},
                            "then": {"range": {"min": 0}},
                            "otherwise": {
                                # only valid for ndim = 0
                                "range": {"min": "when_param"}
                            },
                        }
                    },
                },
                "when_param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "number_dims": 1,
                    "value": [3, 5],
                },
            }

        with pytest.raises(ParamToolsError) as excinfo:
            Params(array_first=True)

        cause = excinfo.value.__cause__
        msg = cause.args[0]
        assert (
            msg
            == "param is validated against when_param in an invalid context."
        )

        class Params(Parameters):
            defaults = {
                "param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "number_dims": 1,
                    "value": [0, 0],
                    "validators": {
                        "when": {
                            "param": "default",
                            "is": {"less_than": 0},
                            "then": {"range": {"min": 0}},
                            "otherwise": {
                                # only valid for ndim = 0
                                "range": {"min": "default"}
                            },
                        }
                    },
                }
            }

        with pytest.raises(ParamToolsError) as excinfo:
            Params(array_first=True)

        cause = excinfo.value.__cause__
        msg = cause.args[0]
        assert (
            msg == "param is validated against default in an invalid context."
        )

    def test_when_validation_examples(self, TestParams):
        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust({"when_param": 2})

        params = TestParams()
        with pytest.raises(ValidationError):
            params.adjust({"when_array_param": [0, 2, 0, 0]})

        params = TestParams()
        with pytest.raises(ValidationError):
            params.adjust({"when_array_param": [0, 1, 0]})

        params = TestParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust({"float_list_when_param": [-1, 0, 0, 0]})

        msg = json.loads(excinfo.value.args[0])
        assert len(msg["errors"]["float_list_when_param"]) == 4

    def test_when_validation_referential(self):
        """
        Test referential validation with when validator.

        Check limitations to referential validation with when validator
        in test test_when_validation_limitations
        """

        class Params(Parameters):
            defaults = {
                "param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "value": 3,
                    "validators": {
                        "when": {
                            "param": "when_param",
                            "is": {"less_than": 0},
                            "then": {"range": {"min": 0}},
                            "otherwise": {
                                # only valid for ndim = 0
                                "range": {"min": "when_param"}
                            },
                        }
                    },
                },
                "when_param": {
                    "title": "",
                    "description": "",
                    "type": "int",
                    "value": 3,
                },
            }

        params = Params(array_first=True)
        params.adjust({"param": 4})
        params.adjust({"param": 0, "when_param": -1})

        params = Params(array_first=True)
        with pytest.raises(ValidationError):
            params.adjust({"param": -1, "when_param": -2})

        params = Params(array_first=True)
        with pytest.raises(ValidationError):
            params.adjust({"param": params.when_param - 1})

    def test_deserialized(self, TestParams):
        params = TestParams()
        params._adjust({"min_int_param": [{"value": 1}]}, deserialized=True)
        assert params.min_int_param == [
            {"label0": "zero", "label1": 1, "value": 1},
            {"label0": "one", "label1": 2, "value": 1},
        ]

        params._adjust(
            {"min_int_param": [{"value": -1}]},
            raise_errors=False,
            deserialized=True,
        )

        assert params.errors["min_int_param"] == ["min_int_param -1 < min 0 "]


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

        val = params.sel["int_dense_array_param"].isel[0]
        labels = {lab: val for lab, val in val.items() if lab != "value"}
        params.delete({"int_dense_array_param": [dict(labels, value=None)]})

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
            {"label0": "zero", "label2": 0, "value": 1},
            {"label0": "zero", "label2": 1, "value": 1},
            {"label0": "zero", "label2": 2, "value": 1},
            {"label0": "one", "label2": 0, "value": 1},
            {"label0": "one", "label2": 1, "value": 1},
            {"label0": "one", "label2": 2, "value": 1},
        ]

        params = TestParams()
        params.madeup = vi
        params._data["madeup"] = {"value": vi, "type": "int"}
        value_items = params.select_eq("madeup", False, **params._state)
        assert params._resolve_order(
            "madeup", value_items, params.label_grid
        ) == (exp_label_order, exp_value_order)

        # test with specified state.
        exp_value_order = {"label0": ["zero", "one"], "label2": [0, 1]}
        params.set_state(label2=[0, 1])
        value_items = params.select_eq("madeup", False, **params._state)
        assert params._resolve_order(
            "madeup", value_items, params.label_grid
        ) == (exp_label_order, exp_value_order)

        params.madeup[0]["label1"] = 0
        value_items = params.select_eq("madeup", False, **params._state)
        with pytest.raises(InconsistentLabelsException):
            params._resolve_order("madeup", value_items, params.label_grid)

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

        assert (
            params.from_array("int_dense_array_param", res)
            == params.int_dense_array_param
        )

        params = TestParams()
        res = params.to_array("int_dense_array_param", label0="zero")

        assert res.tolist() == exp

        act = copy.deepcopy(
            params.from_array("int_dense_array_param", res, label0="zero")
        )
        params.set_state(label0="zero")
        assert act == params.int_dense_array_param

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

        assert (
            params.from_array("int_dense_array_param", res)
            == params.int_dense_array_param
        )

        params = TestParams()
        res = params.to_array("int_dense_array_param", label1=[0, 1, 2, 5])

        assert res.tolist() == exp

        act = copy.deepcopy(
            params.from_array(
                "int_dense_array_param", res, label1=[0, 1, 2, 5]
            )
        )
        params.set_state(label1=[0, 1, 2, 5])
        assert act == params.int_dense_array_param


class TestState:
    def test_basic_set_state(self, TestParams):
        params = TestParams()
        assert params.view_state() == {}
        params.set_state(label0="zero")
        assert params.view_state() == {"label0": ["zero"]}
        params.set_state(label1=0)
        assert params.view_state() == {"label0": ["zero"], "label1": [0]}
        params.set_state(label0="one", label2=1)
        assert params.view_state() == {
            "label0": ["one"],
            "label1": [0],
            "label2": [1],
        }
        params.set_state(**{})
        assert params.view_state() == {
            "label0": ["one"],
            "label1": [0],
            "label2": [1],
        }
        params.set_state()
        assert params.view_state() == {
            "label0": ["one"],
            "label1": [0],
            "label2": [1],
        }
        params.set_state(label1=[1, 2, 3])
        assert params.view_state() == {
            "label0": ["one"],
            "label1": [1, 2, 3],
            "label2": [1],
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
        assert af_params.str_choice_param == "value0"

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

    def test_to_array_with_nd_lists(self):
        class ArrayAdjust(Parameters):
            defaults = {
                "schema": {
                    "labels": {
                        "label1": {
                            "type": "int",
                            "validators": {"range": {"min": 0, "max": 5}},
                        }
                    }
                },
                "arr": {
                    "title": "Array param",
                    "description": "",
                    "type": "float",
                    "number_dims": 1,
                    "value": [1, 2, 3, 4],
                },
                "arr_2D": {
                    "title": "2D Array Param",
                    "description": "",
                    "type": "int",
                    "number_dims": 2,
                    "value": [[1, 2, 3], [4, 5, 6]],
                },
            }
            array_first = True

        params = ArrayAdjust()
        assert params
        assert isinstance(params.arr, np.ndarray)
        assert params.arr.tolist() == [1, 2, 3, 4]
        assert isinstance(params.arr_2D, np.ndarray)
        assert params.arr_2D.tolist() == [[1, 2, 3], [4, 5, 6]]

        params.adjust({"arr": [4, 6, 8], "arr_2D": [[7, 8, 9], [1, 5, 7]]})
        assert isinstance(params.arr, np.ndarray)
        assert isinstance(params.arr_2D, np.ndarray)
        np.testing.assert_allclose(params.arr, [4, 6, 8])
        np.testing.assert_allclose(params.arr_2D, [[7, 8, 9], [1, 5, 7]])

        with pytest.raises(ParamToolsError):
            params.adjust({"arr": [{"label1": 1, "value": [4, 5, 6]}]})

    def test_array_first_with_zero_dim(self):
        class ZeroDim(Parameters):
            defaults = {
                "myint": {
                    "title": "my int",
                    "description": "",
                    "type": "int",
                    "value": 2,
                },
                "mystring": {
                    "title": "my string",
                    "description": "",
                    "type": "str",
                    "value": "hello world",
                },
            }
            array_first = True

        params = ZeroDim()
        assert params.myint == 2.0
        assert isinstance(params.myint, np.int64)

        assert params.mystring == "hello world"
        assert isinstance(params.mystring, str)


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


class TestExtend:
    def test_extend_num(self, array_first_defaults):
        array_first_defaults = {
            "schema": array_first_defaults["schema"],
            "int_dense_array_param": array_first_defaults[
                "int_dense_array_param"
            ],
        }
        new_vos = []
        for vo in array_first_defaults["int_dense_array_param"]["value"]:
            if vo["label1"] not in (2, 4, 5):
                new_vos.append(vo)

        array_first_defaults["int_dense_array_param"]["value"] = new_vos

        # Where label 1 is 2, 4, and 5, the value is set to the last
        # known value, given the value object's label values.
        exp = [
            {"label0": "zero", "label1": 0, "label2": 0, "value": 1},
            {"label0": "zero", "label1": 0, "label2": 1, "value": 2},
            {"label0": "zero", "label1": 0, "label2": 2, "value": 3},
            {"label0": "zero", "label1": 1, "label2": 0, "value": 4},
            {"label0": "zero", "label1": 1, "label2": 1, "value": 5},
            {"label0": "zero", "label1": 1, "label2": 2, "value": 6},
            {"label0": "zero", "label1": 2, "label2": 0, "value": 4},
            {"label0": "zero", "label1": 2, "label2": 1, "value": 5},
            {"label0": "zero", "label1": 2, "label2": 2, "value": 6},
            {"label0": "zero", "label1": 3, "label2": 0, "value": 10},
            {"label0": "zero", "label1": 3, "label2": 1, "value": 11},
            {"label0": "zero", "label1": 3, "label2": 2, "value": 12},
            {"label0": "zero", "label1": 4, "label2": 0, "value": 10},
            {"label0": "zero", "label1": 4, "label2": 1, "value": 11},
            {"label0": "zero", "label1": 4, "label2": 2, "value": 12},
            {"label0": "zero", "label1": 5, "label2": 0, "value": 10},
            {"label0": "zero", "label1": 5, "label2": 1, "value": 11},
            {"label0": "zero", "label1": 5, "label2": 2, "value": 12},
            {"label0": "one", "label1": 0, "label2": 0, "value": 19},
            {"label0": "one", "label1": 0, "label2": 1, "value": 20},
            {"label0": "one", "label1": 0, "label2": 2, "value": 21},
            {"label0": "one", "label1": 1, "label2": 0, "value": 22},
            {"label0": "one", "label1": 1, "label2": 1, "value": 23},
            {"label0": "one", "label1": 1, "label2": 2, "value": 24},
            {"label0": "one", "label1": 2, "label2": 0, "value": 22},
            {"label0": "one", "label1": 2, "label2": 1, "value": 23},
            {"label0": "one", "label1": 2, "label2": 2, "value": 24},
            {"label0": "one", "label1": 3, "label2": 0, "value": 28},
            {"label0": "one", "label1": 3, "label2": 1, "value": 29},
            {"label0": "one", "label1": 3, "label2": 2, "value": 30},
            {"label0": "one", "label1": 4, "label2": 0, "value": 28},
            {"label0": "one", "label1": 4, "label2": 1, "value": 29},
            {"label0": "one", "label1": 4, "label2": 2, "value": 30},
            {"label0": "one", "label1": 5, "label2": 0, "value": 28},
            {"label0": "one", "label1": 5, "label2": 1, "value": 29},
            {"label0": "one", "label1": 5, "label2": 2, "value": 30},
        ]

        class AFParams(Parameters):
            defaults = array_first_defaults
            label_to_extend = "label1"
            array_first = True

        params = AFParams()
        assert isinstance(params.int_dense_array_param, np.ndarray)
        assert params.from_array("int_dense_array_param") == exp
        for val in params._data["int_dense_array_param"]["value"]:
            if val["label1"] in (2, 4, 5):
                assert val["_auto"] is True
            else:
                assert "_auto" not in val

        assert params.dump()["int_dense_array_param"]["value"] == exp

        class AFParams(Parameters):
            defaults = array_first_defaults
            label_to_extend = "label1"
            array_first = False

        params = AFParams()
        assert isinstance(params.int_dense_array_param, list)

    def test_extend_categorical(self, array_first_defaults):
        array_first_defaults = {
            "schema": array_first_defaults["schema"],
            "int_dense_array_param": array_first_defaults[
                "int_dense_array_param"
            ],
        }
        new_vos = []
        for vo in array_first_defaults["int_dense_array_param"]["value"]:
            if vo["label0"] == "one":
                vo.update({"value": vo["value"] - 18})
                new_vos.append(vo)

        array_first_defaults["int_dense_array_param"]["value"] = new_vos

        class AFParams(Parameters):
            defaults = array_first_defaults
            label_to_extend = "label0"
            array_first = True

        params = AFParams()
        assert params.int_dense_array_param.tolist()
        exp = [
            {"label0": "one", "label1": 0, "label2": 0, "value": 1},
            {"label0": "one", "label1": 0, "label2": 1, "value": 2},
            {"label0": "one", "label1": 0, "label2": 2, "value": 3},
            {"label0": "one", "label1": 1, "label2": 0, "value": 4},
            {"label0": "one", "label1": 1, "label2": 1, "value": 5},
            {"label0": "one", "label1": 1, "label2": 2, "value": 6},
            {"label0": "one", "label1": 2, "label2": 0, "value": 7},
            {"label0": "one", "label1": 2, "label2": 1, "value": 8},
            {"label0": "one", "label1": 2, "label2": 2, "value": 9},
            {"label0": "one", "label1": 3, "label2": 0, "value": 10},
            {"label0": "one", "label1": 3, "label2": 1, "value": 11},
            {"label0": "one", "label1": 3, "label2": 2, "value": 12},
            {"label0": "one", "label1": 4, "label2": 0, "value": 13},
            {"label0": "one", "label1": 4, "label2": 1, "value": 14},
            {"label0": "one", "label1": 4, "label2": 2, "value": 15},
            {"label0": "one", "label1": 5, "label2": 0, "value": 16},
            {"label0": "one", "label1": 5, "label2": 1, "value": 17},
            {"label0": "one", "label1": 5, "label2": 2, "value": 18},
        ]
        assert params.from_array("int_dense_array_param", label0="one") == exp

        for val in params._data["int_dense_array_param"]["value"]:
            if val["label0"] == "zero":
                assert val["_auto"] is True
            else:
                assert "_auto" not in val

    def test_extend_w_array(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True

        params = ExtParams()

        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [3, 4],
            [3, 4],
            [5, 6],
            [5, 6],
            [7, 8],
            [7, 8],
            [7, 8],
            [7, 8],
        ]

    def test_extend_adj(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True

        params = ExtParams()
        params.adjust({"extend_param": [{"d0": 3, "value": -1}]})

        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
        ]

        for val in params._data["extend_param"]["value"]:
            # 0, 1 extended at the beginning.
            if val["d0"] > 3 or val["d0"] in (0, 1):
                assert val["_auto"] is True
            else:
                assert "_auto" not in val

        params = ExtParams()
        params.adjust(
            {
                "extend_param": [
                    {"d0": 3, "d1": "c1", "value": -1},
                    {"d0": 3, "d1": "c2", "value": 1},
                ]
            }
        )

        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, 1],
            [-1, 1],
            [-1, 1],
            [-1, 1],
            [-1, 1],
            [-1, 1],
            [-1, 1],
            [-1, 1],
        ]

        params = ExtParams()
        params.adjust(
            {
                "extend_param": [
                    {"d0": 3, "value": -1},
                    {"d0": 5, "d1": "c1", "value": 0},
                    {"d0": 5, "d1": "c2", "value": 1},
                    {"d0": 8, "d1": "c1", "value": 22},
                    {"d0": 8, "d1": "c2", "value": 23},
                ]
            }
        )

        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, -1],
            [-1, -1],
            [0, 1],
            [0, 1],
            [0, 1],
            [22, 23],
            [22, 23],
            [22, 23],
        ]

        params = ExtParams()
        params.adjust(
            {
                "extend_param": [
                    {"d0": 3, "value": -1},
                    {"d0": 5, "d1": "c1", "value": 0},
                    {"d0": 6, "d1": "c2", "value": 1},
                ]
            }
        )
        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, -1],
            [-1, -1],
            [0, -1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
        ]

        params = ExtParams()
        params.adjust({"extend_param": [{"d0": 0, "value": 1}]})
        assert params.extend_param.tolist() == [[1, 1]] * 11

    def test_extend_adj_without_clobber(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True

        params = ExtParams()
        params.adjust(
            {"extend_param": [{"d0": 3, "value": -1}]}, clobber=False
        )
        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, -1],
            [-1, -1],
            [5, 6],
            [5, 6],
            [7, 8],
            [7, 8],
            [7, 8],
            [7, 8],
        ]

        params = ExtParams()
        params.adjust(
            {
                "extend_param": [
                    {"d0": 3, "d1": "c1", "value": -1},
                    {"d0": 3, "d1": "c2", "value": 1},
                ]
            },
            clobber=False,
        )

        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, 1],
            [-1, 1],
            [5, 6],
            [5, 6],
            [7, 8],
            [7, 8],
            [7, 8],
            [7, 8],
        ]

        params = ExtParams()
        params.adjust(
            {
                "extend_param": [
                    {"d0": 3, "value": -1},
                    {"d0": 5, "d1": "c1", "value": 0},
                    {"d0": 5, "d1": "c2", "value": 1},
                    {"d0": 8, "d1": "c1", "value": 22},
                    {"d0": 8, "d1": "c2", "value": 23},
                ]
            },
            clobber=False,
        )

        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, -1],
            [-1, -1],
            [0, 1],
            [0, 1],
            [7, 8],
            [22, 23],
            [22, 23],
            [22, 23],
        ]

        params = ExtParams()
        params.adjust(
            {
                "extend_param": [
                    {"d0": 3, "value": -1},
                    {"d0": 5, "d1": "c1", "value": 0},
                    {"d0": 6, "d1": "c2", "value": 1},
                ]
            },
            clobber=False,
        )
        assert params.extend_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [-1, -1],
            [-1, -1],
            [0, 6],
            [0, 1],
            [7, 8],
            [7, 8],
            [7, 8],
            [7, 8],
        ]

        params = ExtParams()
        params.adjust({"extend_param": [{"d0": 0, "value": 1}]}, clobber=False)
        assert params.extend_param.tolist() == [
            [1, 1],
            [1, 1],
            [1, 2],
            [3, 4],
            [3, 4],
            [5, 6],
            [5, 6],
            [7, 8],
            [7, 8],
            [7, 8],
            [7, 8],
        ]

    def test_extend_adj_w_errors(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True

        params = ExtParams()
        with pytest.raises(ValidationError):
            params.adjust({"extend_param": 102})

        params = ExtParams()
        with pytest.raises(ValidationError) as excinfo:
            params.adjust({"extend_param": [{"value": 70, "d0": 5}]})

        emsg = json.loads(excinfo.value.args[0])
        # do=7 is when the 'releated_value' is set to 50, which is
        # less than 70 ==> causes range error
        assert "d0=7" in emsg["errors"]["extend_param"][0]
        params = ExtParams()
        before = copy.deepcopy(params.extend_param)
        params.adjust(
            {"extend_param": [{"value": 70, "d0": 5}]}, raise_errors=False
        )
        assert params.errors["extend_param"] == emsg["errors"]["extend_param"]
        assert np.allclose(params.extend_param, before)

    def test_extend_adj_nonextend_param(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True

        params = ExtParams()
        params.adjust({"nonextend_param": 3})
        assert params.nonextend_param == 3

    def test_extend_adj_w_set_state(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True

        params = ExtParams()
        params.set_state(d0=list(range(2, 11)))
        params.adjust({"extend_param": [{"d0": 2, "value": -1}]})

        assert params.extend_param.tolist() == [
            # [1, 2],
            # [1, 2],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
        ]

        params = ExtParams()
        params.set_state(d0=list(range(2, 11)))
        params.adjust({"extend_param": [{"d0": 3, "value": -1}]})

        assert params.extend_param.tolist() == [
            # [1, 2],
            # [1, 2],
            [1, 2],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
        ]

        params = ExtParams()
        params.set_state(d0=list(range(2, 11)))
        params.adjust({"extend_param": [{"d0": 1, "value": -1}]})
        assert params.extend_param.tolist() == []
        params.array_first = False
        params.clear_state()
        params.extend()
        params.array_first = True
        params.set_state()
        assert params.extend_param.tolist() == [
            [1, 2],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
            [-1, -1],
        ]

    def test_extend_method(self, extend_ex_path):
        class ExtParams(Parameters):
            defaults = extend_ex_path
            # label_to_extend = "d0"
            array_first = False

        params = ExtParams()
        params.adjust({"extend_param": [{"value": None}]})
        params.adjust(
            {
                "extend_param": [
                    {"d0": 2, "d1": "c1", "value": 1},
                    {"d0": 2, "d1": "c2", "value": 2},
                ]
            }
        )
        params.extend(
            label="d0", label_values=[2, 4, 7], params="extend_param"
        )
        params.sort_values()
        assert params.extend_param == [
            {"d0": 2, "d1": "c1", "value": 1},
            {"d0": 2, "d1": "c2", "value": 2},
            {"d0": 4, "d1": "c1", "value": 1, "_auto": True},
            {"d0": 4, "d1": "c2", "value": 2, "_auto": True},
            {"d0": 7, "d1": "c1", "value": 1, "_auto": True},
            {"d0": 7, "d1": "c2", "value": 2, "_auto": True},
        ]

        params = ExtParams()
        init = params.select_eq("extend_param")
        params.extend(label="d0", label_values=[])
        assert init == params.select_eq("extend_param")

        params = ExtParams()
        params.extend(label="d0", label_values=[8, 9, 10])
        params.sort_values()
        assert params.extend_param == [
            {"d0": 2, "d1": "c1", "value": 1},
            {"d0": 2, "d1": "c2", "value": 2},
            {"d0": 3, "d1": "c1", "value": 3},
            {"d0": 3, "d1": "c2", "value": 4},
            {"d0": 5, "d1": "c1", "value": 5},
            {"d0": 5, "d1": "c2", "value": 6},
            {"d0": 7, "d1": "c1", "value": 7},
            {"d0": 7, "d1": "c2", "value": 8},
            {"d0": 8, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 8, "d1": "c2", "value": 8, "_auto": True},
            {"d0": 9, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 9, "d1": "c2", "value": 8, "_auto": True},
            {"d0": 10, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 10, "d1": "c2", "value": 8, "_auto": True},
        ]

        params = ExtParams()
        params.extend(label="d0", label_values=[0, 8, 9, 10])
        params.sort_values()
        assert params.extend_param == [
            {"d0": 0, "d1": "c1", "value": 1, "_auto": True},
            {"d0": 0, "d1": "c2", "value": 2, "_auto": True},
            {"d0": 2, "d1": "c1", "value": 1},
            {"d0": 2, "d1": "c2", "value": 2},
            {"d0": 3, "d1": "c1", "value": 3},
            {"d0": 3, "d1": "c2", "value": 4},
            {"d0": 5, "d1": "c1", "value": 5},
            {"d0": 5, "d1": "c2", "value": 6},
            {"d0": 7, "d1": "c1", "value": 7},
            {"d0": 7, "d1": "c2", "value": 8},
            {"d0": 8, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 8, "d1": "c2", "value": 8, "_auto": True},
            {"d0": 9, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 9, "d1": "c2", "value": 8, "_auto": True},
            {"d0": 10, "d1": "c1", "value": 7, "_auto": True},
            {"d0": 10, "d1": "c2", "value": 8, "_auto": True},
        ]


def grow(n, r, t):
    mult = 1 if t >= 0 else -1
    for _ in range(0, abs(t)):
        n = round(n * (1 + r) ** mult, 2)
    return n


class TestIndex:
    def test_index_simple(self, extend_ex_path):
        class IndexParams1(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True
            uses_extend_func = True
            index_rates = {lte: 0 for lte in range(10)}

        params = IndexParams1()
        params.adjust({"indexed_param": [{"d0": 3, "value": 3}]})

        assert params.indexed_param.tolist() == [
            [1, 2],
            [1, 2],
            [1, 2],
            [3, 3],
            [3, 3],
            [3, 3],
            [3, 3],
            [3, 3],
            [3, 3],
            [3, 3],
            [3, 3],
        ]

        for val in params._data["indexed_param"]["value"]:
            # 0, 1 extended at the beginning.
            if val["d0"] > 3 or val["d0"] in (0, 1):
                assert val["_auto"] is True
            else:
                assert "_auto" not in val

        class IndexParams2(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True
            uses_extend_func = True
            index_rates = {lte: 0.02 for lte in range(10)}

        params = IndexParams2()
        params.adjust({"indexed_param": [{"d0": 3, "value": 3}]})
        exp = [
            [grow(1, 0.02, -2), grow(2, 0.02, -2)],
            [grow(1, 0.02, -1), grow(2, 0.02, -1)],
            [grow(1, 0.02, 0), grow(2, 0.02, 0)],
            [grow(3, 0.02, 0)] * 2,
            [grow(3, 0.02, 1)] * 2,
            [grow(3, 0.02, 2)] * 2,
            [grow(3, 0.02, 3)] * 2,
            [grow(3, 0.02, 4)] * 2,
            [grow(3, 0.02, 5)] * 2,
            [grow(3, 0.02, 6)] * 2,
            [grow(3, 0.02, 7)] * 2,
        ]
        np.testing.assert_allclose(params.indexed_param.tolist(), exp)

    def test_related_param_errors(self, extend_ex_path):
        class IndexParams2(Parameters):
            defaults = extend_ex_path
            label_to_extend = "d0"
            array_first = True
            uses_extend_func = True
            index_rates = {lte: 0.02 for lte in range(10)}

        params = IndexParams2()

        with pytest.raises(ValidationError):
            params.adjust(
                {
                    "related_param": [{"value": 8.1, "d0": 4}],
                    "indexed_param": [{"d0": 3, "value": 8}],
                }
            )
