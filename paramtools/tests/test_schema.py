import copy

import pytest
import marshmallow as ma

from paramtools import (
    get_type,
    get_param_schema,
    register_custom_type,
    ALLOWED_TYPES,
    UnknownTypeException,
    PartialField,
    ParamToolsError,
)


def test_get_type_with_list():
    int_field = get_type({"type": "int"})

    list_int_field = get_type({"type": "int", "number_dims": 1})
    assert list_int_field.np_type == int_field.np_type

    list_int_field = get_type({"type": "int", "number_dims": 2})
    assert list_int_field.np_type == int_field.np_type


def test_register_custom_type():
    """
    Test allowed to register marshmallow field and PartialField instances and
    test that uninitialized fields and random classes throw type errors.
    """
    custom_type = "custom"
    assert custom_type not in ALLOWED_TYPES
    register_custom_type(custom_type, ma.fields.String())
    assert custom_type in ALLOWED_TYPES

    register_custom_type("partial-test", PartialField(ma.fields.Str(), {}))
    assert "partial-test" in ALLOWED_TYPES

    with pytest.raises(TypeError):
        register_custom_type("custom", ma.fields.Str)

    class Whatever:
        pass

    with pytest.raises(TypeError):
        register_custom_type("whatever", Whatever())


def test_get_type():
    custom_type = "custom"
    register_custom_type(custom_type, ma.fields.String())

    assert isinstance(get_type({"type": custom_type}), ma.fields.String)

    with pytest.raises(UnknownTypeException):
        get_type({"type": "unknown"})


def test_make_schema():
    custom_type = "custom"
    register_custom_type(custom_type, ma.fields.String())

    schema = {
        "labels": {"lab": {"type": custom_type, "validators": {}}},
        "additional_members": {"custom": {"type": custom_type}},
    }

    assert get_param_schema(schema)

    bad_schema = copy.deepcopy(schema)
    bad_schema["labels"]["lab"]["type"] = "unknown"
    with pytest.raises(UnknownTypeException):
        get_param_schema(bad_schema)

    bad_schema = copy.deepcopy(schema)
    bad_schema["additional_members"]["custom"]["type"] = "unknown"
    with pytest.raises(UnknownTypeException):
        get_param_schema(bad_schema)

    schema = {
        "labels": {
            "lab": {
                "type": custom_type,
                "validators": {"choice": {"choices": ["hello"]}},
            }
        },
        "additional_members": {"custom": {"type": custom_type}},
    }
    with pytest.raises(ParamToolsError):
        get_param_schema(schema)
