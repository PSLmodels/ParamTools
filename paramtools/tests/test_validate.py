import datetime

import pytest
from marshmallow import ValidationError

from paramtools.contrib import OneOf, Range, DateRange


def test_OneOf():
    choices = ["allowed1", "allowed2"]

    oneof = OneOf(choices=choices)
    assert oneof("allowed1") == "allowed1"
    assert oneof(choices) == choices
    assert oneof([choices]) == [choices]

    with pytest.raises(ValidationError):
        oneof("notallowed")

    with pytest.raises(ValidationError):
        oneof(["notallowed", "allowed1"])

    # no support for 3-D arrays yet.
    with pytest.raises(ValidationError):
        oneof([[choices]])


def test_Range():
    range_ = Range(0, 10)
    assert range_.grid() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    range_ = Range(0, 10, step=3)
    assert range_.grid() == [0, 3, 6, 9]


def test_DateRange():
    drange = DateRange("2019-01-01", "2019-01-10", step={"days": 1})
    exp = [datetime.date(2019, 1, i) for i in range(1, 10 + 1)]
    assert drange.grid() == exp

    drange = DateRange("2019-01-01", "2019-01-10")
    exp = [datetime.date(2019, 1, i) for i in range(1, 10 + 1)]
    assert drange.grid() == exp

    drange = DateRange("2019-01-01", "2019-01-10", step={"days": 3})
    exp = [datetime.date(2019, 1, i) for i in range(1, 10 + 1, 3)]
    assert drange.grid() == exp
