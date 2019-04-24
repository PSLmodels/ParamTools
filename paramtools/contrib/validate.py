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
        self, min=None, max=None, error_min=None, error_max=None, step=None
    ):
        self.min = min
        self.max = max
        self.error_min = error_min
        self.error_max = error_max
        self.step = step or 1  # default to 1

    def _format_error(self, value, message):
        return message.format(input=value, min=self.min, max=self.max)

    def __call__(self, value):
        if value is None:
            return value
        if not isinstance(value, list):
            value_list = [value]
        else:
            value_list = utils.ravel(value)

        for val in value_list:
            if self.min is not None and val < self.min:
                message = self.error_min or self.message_min
                raise ValidationError(self._format_error(value, message))

            if self.max is not None and val > self.max:
                message = self.error_max or self.message_max
                raise ValidationError(self._format_error(value, message))

        return value

    def grid(self):
        # make np.arange inclusive.
        max_ = self.max + self.step
        arr = np.arange(self.min, max_, self.step)
        return arr[arr <= self.max].tolist()


class DateRange(Range):
    """
    Implements "date_range" :ref:`spec:Validator object`.
    Behaves like ``Range``, except values are ensured to be
    ``datetime.date`` type and ``grid`` has special logic for dates.
    """

    def __init__(
        self, min=None, max=None, error_min=None, error_max=None, step=None
    ):
        if min is not None and not isinstance(min, datetime.date):
            min = marshmallow_fields.Date()._deserialize(min, None, None)
        if max is not None and not isinstance(max, datetime.date):
            max = marshmallow_fields.Date()._deserialize(max, None, None)

        super().__init__(min, max, error_min, error_max)

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

    def grid(self):
        # make np.arange inclusive.
        max_ = self.max + self.step
        arr = np.arange(self.min, max_, self.step, dtype=datetime.date)
        return arr[arr <= self.max].tolist()


class OneOf(marshmallow_validate.OneOf):
    """
    Implements "choice" :ref:`spec:Validator object`.
    """

    def __call__(self, value):
        if value is None:
            return value
        if not isinstance(value, list):
            values = [value]
        else:
            values = utils.ravel(value)
        for val in values:
            try:
                if val not in self.choices:
                    raise ValidationError(self._format_error(val))
            except TypeError:
                raise ValidationError(self._format_error(val))
        return value

    def grid(self):
        return self.choices
