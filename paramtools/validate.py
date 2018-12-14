import json

from marshmallow import validate, ValidationError


class OneOfFromFile(validate.OneOf):

    default_message = '"{input}" is not a valid choice.'

    def __init__(self, choicefilepath, labels=None, error=None):
        with open(choicefilepath, "r") as f:
            data = json.loads(f.read())
        super().__init__(data["choices"], labels=labels, error=None)


class Range(validate.Range):
    def __init__(self, min=None, max=None, error_min=None, error_max=None):
        self.min = min
        self.max = max
        self.error_min = error_min
        self.error_max = error_max

    def _format_error(self, value, message):
        return message.format(input=value, min=self.min, max=self.max)

    def __call__(self, value):
        if self.min is not None and value < self.min:
            message = self.error_min or self.message_min
            raise ValidationError(self._format_error(value, message))

        if self.max is not None and value > self.max:
            message = self.error_max or self.message_max
            raise ValidationError(self._format_error(value, message))

        return value
