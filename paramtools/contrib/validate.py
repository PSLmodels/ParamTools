import datetime

import numpy as np
from marshmallow import (
    validate as marshmallow_validate,
    ValidationError,
    fields as marshmallow_fields,
)

from paramtools import utils


class Range(marshmallow_validate.Range):
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
            raise ValidationError(msgs if len(msgs) > 1 else msgs[0])
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

    def safe_deserialize(self, date):
        if isinstance(date, datetime.date):
            return date
        else:
            return marshmallow_fields.Date()._deserialize(date, None, None)

    def grid(self):
        # make np.arange inclusive.
        max_ = self.max[0]["value"] + self.step
        arr = np.arange(
            self.min[0]["value"], max_, self.step, dtype=datetime.date
        )
        return arr[arr <= self.max[0]["value"]].tolist()


class OneOf(marshmallow_validate.OneOf):
    """
    Implements "choice" :ref:`spec:Validator object`.
    """

    default_message = "Input {input} must be one of {choices}"

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
                    raise ValidationError(self._format_error(vo))
            except TypeError:
                raise ValidationError(self._format_error(vo))
        return value

    def grid(self):
        return self.choices
