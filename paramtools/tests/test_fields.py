import datetime

import numpy as np
from marshmallow import ValidationError as MarshmallowVE

from paramtools.contrib import fields, validate


def test_np_value_fields():
    float64 = fields.Float64()
    res = float64._deserialize("2", None, None)
    assert res == 2.0
    assert isinstance(res, np.float64)

    int64 = fields.Int64()
    res = int64._deserialize("2", None, None)
    assert res == 2
    assert isinstance(res, np.int64)

    bool_ = fields.Bool_()
    res = bool_._deserialize("true", None, None)
    assert res == True
    assert isinstance(res, np.bool_)
    assert bool_._serialize(res, None, None) is True


def test_contrib_fields():
    range_validator = validate.Range(0, 10)
    daterange_validator = validate.DateRange(
        "2019-01-01", "2019-01-05", step={"days": 2}
    )
    choice_validator = validate.OneOf(choices=["one", "two"])

    s = fields.Str(validate=[choice_validator])
    assert s.mesh() == ["one", "two"]
    s = fields.Str()
    assert s.mesh() == []

    s = fields.Integer(validate=[range_validator])
    assert s.mesh() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    s = fields.Str()
    assert s.mesh() == []

    # date will need an interval argument.
    s = fields.Date(validate=[daterange_validator])
    assert s.mesh() == [datetime.date(2019, 1, i) for i in range(1, 6, 2)]
