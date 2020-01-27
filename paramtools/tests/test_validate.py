import datetime

import pytest
from marshmallow import ValidationError

from paramtools.contrib import OneOf, Range, DateRange, When


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

    assert oneof("allowed1")
    assert oneof({"value": "allowed1"}, is_value_object=True)

    with pytest.raises(ValidationError):
        oneof("notallowed")

    with pytest.raises(ValidationError):
        oneof({"value": "notallowed"}, is_value_object=True)


def test_Range_errors():
    range_ = Range(0, 10)
    with pytest.raises(ValidationError):
        range_(11)

    with pytest.raises(ValidationError):
        range_({"value": 11}, is_value_object=True)

    range_ = Range(min_vo=[{"value": 0}], max_vo=[{"value": 10}])
    with pytest.raises(ValidationError):
        range_(11)

    with pytest.raises(ValidationError):
        range_({"value": 11}, is_value_object=True)

    range_ = Range(
        min_vo=[{"lab0": 1, "value": 0}, {"lab0": 2, "value": 2}],
        max_vo=[{"lab0": 1, "value": 10}, {"lab0": 2, "value": 9}],
        error_min="param{labels} {input} < min {min} oth_param{oth_labels}",
        error_max="param{labels} {input} > max {max} max_oth_param{oth_labels}",
    )
    with pytest.raises(ValidationError) as excinfo:
        range_({"lab0": 1, "value": 11}, is_value_object=True)
    assert (
        excinfo.value.args[0][0]
        == "param[lab0=1] 11 > max 10 max_oth_param[lab0=1]"
    )

    with pytest.raises(ValidationError) as excinfo:
        range_({"value": 11}, is_value_object=True)
    assert excinfo.value.args[0] == [
        "param 11 > max 10 max_oth_param[lab0=1]",
        "param 11 > max 9 max_oth_param[lab0=2]",
    ]


def test_Range_grid():
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

    dranges = [
        DateRange("2019-01-01", "2019-01-10", step={"days": 1}),
        DateRange(
            min_vo=[{"value": "2019-01-01"}],
            max_vo=[{"value": "2019-01-10"}],
            step={"days": 1},
        ),
    ]
    for drange in dranges:
        assert drange(datetime.date(2019, 1, 2))
        assert drange(
            {"value": datetime.date(2019, 1, 2)}, is_value_object=True
        )

        with pytest.raises(ValidationError):
            drange(datetime.date(2020, 1, 2))

        with pytest.raises(ValidationError):
            drange({"value": datetime.date(2020, 1, 2)}, is_value_object=True)


def test_When():
    range_ = Range(0, 10)
    choices = [12, 15]
    oneof = OneOf(choices=choices)
    when = When(
        {"equal_to": "world"},
        when_vos=[{"value": "hello"}],
        then_validators=[range_],
        otherwise_validators=[oneof],
    )

    when(12)

    with pytest.raises(ValidationError):
        when(3)

    when = When(
        {"equal_to": "hello"},
        when_vos=[{"value": "hello"}],
        then_validators=[range_],
        otherwise_validators=[oneof],
    )

    when(3)

    with pytest.raises(ValidationError):
        when(12)

    assert when.grid() == list(range(10 + 1))


def test_level():
    oneof = OneOf(choices=["allowed1", "allowed2"], level="warn")
    assert oneof.level == "warn"
    with pytest.raises(ValidationError) as excinfo:
        oneof("notachoice")
    assert excinfo.value.level == "warn"

    range_ = Range(0, 10, level="warn")
    assert range_.level == "warn"
    with pytest.raises(ValidationError) as excinfo:
        range_(11)
    assert excinfo.value.level == "warn"
