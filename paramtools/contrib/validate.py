import json

from marshmallow import validate, ValidationError, fields


class Range(validate.Range):
    def __init__(self, min=None, max=None, error_min=None, error_max=None):
        self.min = min
        self.max = max
        self.error_min = error_min
        self.error_max = error_max

    def _format_error(self, value, message):
        return message.format(input=value, min=self.min, max=self.max)

    def __call__(self, value):
        print(value, self.min, self.max)
        if self.min is not None and value < self.min:
            message = self.error_min or self.message_min
            raise ValidationError(self._format_error(value, message))

        if self.max is not None and value > self.max:
            message = self.error_max or self.message_max
            raise ValidationError(self._format_error(value, message))

        return value


class DateRange(Range):
    """
    Mimic behavior in Range above, but tries to cast min/max values to "Date" 
    first.
    """

    def __init__(self, min=None, max=None, error_min=None, error_max=None):
        if min is not None:
            min = fields.Date()._deserialize(min, None, None)
        if max is not None:
            max = fields.Date()._deserialize(min, None, None)
        print(min, max)
        super().__init__(self, min, max, error_min, error_max)
