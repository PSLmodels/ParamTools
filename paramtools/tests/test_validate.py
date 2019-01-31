import pytest
from marshmallow import ValidationError

from paramtools.contrib import OneOf


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
