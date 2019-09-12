from paramtools import get_type


def test_get_type_with_list():
    int_field = get_type({"type": "int"})

    list_int_field = get_type({"type": "int", "number_dims": 1})
    assert list_int_field.np_type == int_field.np_type

    list_int_field = get_type({"type": "int", "number_dims": 2})
    assert list_int_field.np_type == int_field.np_type
