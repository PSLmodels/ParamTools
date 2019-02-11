import datetime

from marshmallow import (
    validate as marshmallow_validate,
    ValidationError,
    fields as marshmallow_fields,
)

from paramtools import utils


class Range(marshmallow_validate.Range):
    error = ""

    def __init__(self, min=None, max=None, error_min=None, error_max=None):
        self.min = min
        self.max = max
        self.error_min = error_min
        self.error_max = error_max

    def _format_error(self, value, message):
        return message.format(input=value, min=self.min, max=self.max)

    def __call__(self, value):
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

    def mesh(self):
        return list(range(self.min, self.max + 1))


class DateRange(Range):
    """
    Mimic behavior in Range above, but tries to cast min/max values to "Date"
    first.
    """

    def __init__(self, min=None, max=None, error_min=None, error_max=None):
        if min is not None and not isinstance(min, datetime.date):
            min = marshmallow_fields.Date()._deserialize(min, None, None)
        if max is not None and not isinstance(max, datetime.date):
            max = marshmallow_fields.Date()._deserialize(max, None, None)
        super().__init__(min, max, error_min, error_max)

    def mesh(self):
        return None


class OneOf(marshmallow_validate.OneOf):
    def __call__(self, value):
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

    def mesh(self):
        return self.choices
