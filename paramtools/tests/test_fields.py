import datetime

import numpy as np

from paramtools.contrib import fields, validate


def test_np_value_fields():
    float64 = fields.Float64()
    res = float64._deserialize("2", None, None)
    assert res == 2.0
    assert isinstance(res, np.float64)
    assert type(float64._serialize(res, None, None)) == float

    int64 = fields.Int64()
    res = int64._deserialize("2", None, None)
    assert res == 2
    assert isinstance(res, np.int64)
    assert type(int64._serialize(res, None, None)) == int

    bool_ = fields.Bool_()
    res = bool_._deserialize("true", None, None)
    assert res is np.bool_(True)
    assert isinstance(res, np.bool_)
    assert bool_._serialize(res, None, None) is True


def test_contrib_fields():
    range_validator = validate.Range(0, 10)
    daterange_validator = validate.DateRange(
        "2019-01-01", "2019-01-05", step={"days": 2}
    )
    choice_validator = validate.OneOf(choices=["one", "two"])

    s = fields.Str(validate=[choice_validator])
    assert s.grid() == ["one", "two"]
    s = fields.Str()
    assert s.grid() == []

    s = fields.Integer(validate=[range_validator])
    assert s.grid() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    s = fields.Str()
    assert s.grid() == []

    # date will need an interval argument.
    s = fields.Date(validate=[daterange_validator])
    assert s.grid() == [datetime.date(2019, 1, i) for i in range(1, 6, 2)]

    s = fields.Date()
    assert s._deserialize(datetime.date(2015, 1, 1), None, None)


def test_cmp_funcs():
    range_validator = validate.Range(0, 10)
    daterange_validator = validate.DateRange(
        "2019-01-01", "2019-01-05", step={"days": 2}
    )
    choice_validator = validate.OneOf(choices=["one", "two"])

    cases = [
        ("one", "two", fields.Str(validate=[choice_validator])),
        (
            datetime.date(2019, 1, 2),
            datetime.date(2019, 1, 3),
            fields.Date(validate=[daterange_validator]),
        ),
        (2, 5, fields.Integer(validate=[range_validator])),
    ]

    for (min_, max_, field) in cases:
        cmp_funcs = field.cmp_funcs()
        assert cmp_funcs["gt"](min_, max_) is False
        assert cmp_funcs["lt"](min_, max_) is True
        assert cmp_funcs["eq"](min_, max_) is False
        assert cmp_funcs["eq"](max_, max_) is True
        assert cmp_funcs["lte"](max_, max_) is True
        assert cmp_funcs["lte"](min_, max_) is True
        assert cmp_funcs["gte"](max_, min_) is True
