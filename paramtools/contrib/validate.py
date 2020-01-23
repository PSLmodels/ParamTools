from typing import List
from paramtools.typing import ValueObject
import datetime

import numpy as np
import marshmallow as ma

from paramtools import utils


class ValidationError(ma.ValidationError):
    def __init__(self, *args, level=None, **kwargs):
        self.level = level or "error"
        super().__init__(*args, **kwargs)


class When(ma.validate.Validator):
    def __init__(
        self,
        is_val,
        when_vos: List[ValueObject],
        then_validators: List[ma.validate.Validator],
        otherwise_validators: List[ma.validate.Validator],
    ):
        self.is_val = is_val
        self.when_vos = when_vos
        self.then_validators = then_validators
        self.otherwise_validators = otherwise_validators

    def __call__(self, value, is_value_object=False):
        if value is None:
            return value
        if not is_value_object:
            value = {"value": value}
        for vo in self.when_vos:
            if vo["value"] == self.is_val:
                for validator in self.then_validators:
                    validator(value, is_value_object=True)
            else:
                for validator in self.otherwise_validators:
                    validator(value, is_value_object=True)

    def grid(self):
        """
        Just return grid of first validator. It's unlikely that
        there will be multiple.
        """
        return self.then_validators[0].grid()


class Range(ma.validate.Range):
    """
    Implements "range" :ref:`spec:Validator object`.
    """

    error = ""

    def __init__(
        self,
        min=None,
        max=None,
        min_vo=None,
        max_vo=None,
        error_min=None,
        error_max=None,
        step=None,
        level=None,
    ):
        if min is not None:
            self.min = [{"value": min}]
        else:
            self.min = min_vo
        if max is not None:
            self.max = [{"value": max}]
        else:
            self.max = max_vo

        self.error_min = error_min
        self.error_max = error_max
        self.step = step or 1  # default to 1

        self.min_inclusive = None
        self.max_inclusive = None
        self.level = level or "error"

    def __call__(self, value, is_value_object=False):
        """
        This is the method that marshmallow calls by default. is_value_object
        validation goes straight to validate_value_objects.
        """
        if value is None:
            return value
        if not is_value_object:
            value = {"value": value}
        return self.validate_value_objects(value)

    def validate_value_objects(self, value):
        if value["value"] is None:
            return None
        msgs = []
        if self.min is not None:
            for min_vo in self.min:
                if np.any(np.array(value["value"]) < min_vo["value"]):
                    msgs.append(
                        (self.error_min or self.message_min).format(
                            input=value["value"],
                            min=min_vo["value"],
                            min_op="less than",
                            labels=utils.make_label_str(value),
                            oth_labels=utils.make_label_str(min_vo),
                        )
                    )
        if self.max is not None:
            for max_vo in self.max:
                if np.any(np.array(value["value"]) > max_vo["value"]):
                    msgs.append(
                        (self.error_max or self.message_max).format(
                            input=value["value"],
                            max=max_vo["value"],
                            max_op="greater than",
                            labels=utils.make_label_str(value),
                            oth_labels=utils.make_label_str(max_vo),
                        )
                    )
        if msgs:
            raise ValidationError(
                msgs if len(msgs) > 1 else msgs[0], level=self.level
            )
        return value

    def grid(self):
        # make np.arange inclusive.
        max_ = self.max[0]["value"] + self.step
        arr = np.arange(self.min[0]["value"], max_, self.step)
        return arr[arr <= self.max[0]["value"]].tolist()


class DateRange(Range):
    """
    Implements "date_range" :ref:`spec:Validator object`.
    Behaves like ``Range``, except values are ensured to be
    ``datetime.date`` type and ``grid`` has special logic for dates.
    """

    def __init__(
        self,
        min=None,
        max=None,
        min_vo=None,
        max_vo=None,
        error_min=None,
        error_max=None,
        step=None,
        level=None,
    ):
        if min is not None:
            self.min = [{"value": self.safe_deserialize(min)}]
        elif min_vo is not None:
            self.min = [
                dict(vo, **{"value": self.safe_deserialize(vo["value"])})
                for vo in min_vo
            ]
        else:
            self.min = None

        if max is not None:
            self.max = [{"value": self.safe_deserialize(max)}]
        elif max_vo is not None:
            self.max = [
                dict(vo, **{"value": self.safe_deserialize(vo["value"])})
                for vo in max_vo
            ]
        else:
            self.max = None

        self.error_min = error_min
        self.error_max = error_max

        if step is None:
            # set to to default step.
            step = {"days": 1}
        # check against allowed args:
        # https://docs.python.org/3/library/datetime.html#datetime.timedelta
        timedelta_args = {
            "days",
            "seconds",
            "microseconds",
            "milliseconds",
            "minutes",
            "hours",
            "weeks",
        }
        assert len(set(step.keys()) - timedelta_args) == 0
        self.step = datetime.timedelta(**step)

        self.level = level or "error"

    def safe_deserialize(self, date):
        if isinstance(date, datetime.date):
            return date
        else:
            return ma.fields.Date()._deserialize(date, None, None)

    def grid(self):
        # make np.arange inclusive.
        max_ = self.max[0]["value"] + self.step
        arr = np.arange(
            self.min[0]["value"], max_, self.step, dtype=datetime.date
        )
        return arr[arr <= self.max[0]["value"]].tolist()


class OneOf(ma.validate.OneOf):
    """
    Implements "choice" :ref:`spec:Validator object`.
    """

    default_message = "Input {input} must be one of {choices}"

    def __init__(self, *args, level=None, **kwargs):
        self.level = level or "error"
        super().__init__(*args, **kwargs)

    def __call__(self, value, is_value_object=False):
        if value is None:
            return value
        if not is_value_object:
            vo = {"value": value}
        else:
            vo = value
        if vo["value"] is None:
            return None
        if not isinstance(vo["value"], list):
            vos = {"value": [vo["value"]]}
        else:
            vos = {"value": utils.ravel(vo["value"])}
        for vo in vos["value"]:
            try:
                if vo not in self.choices:
                    raise ValidationError(
                        self._format_error(vo), level=self.level
                    )
            except TypeError:
                raise ValidationError(self._format_error(vo), level=self.level)
        return value

    def grid(self):
        return self.choices
