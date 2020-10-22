from typing import List
import datetime
import itertools

from dateutil.relativedelta import relativedelta
import numpy as np
import marshmallow as ma

from paramtools.typing import ValueObject
from paramtools import utils


class ValidationError(ma.ValidationError):
    def __init__(self, *args, level=None, **kwargs):
        self.level = level or "error"
        super().__init__(*args, **kwargs)


class When(ma.validate.Validator):
    then_message = "When value is {is_val}, the input is invalid: {submsg}"
    otherwise_message = (
        "When value is {is_val}, the input is invalid: {submsg}"
    )
    shape_mismatch = "Shape mismatch between parameters: {shape1} {shape2}"

    is_value_evaluators = {
        "equal_to": lambda when_value, is_val: when_value == is_val,
        "less_than": lambda when_value, is_val: when_value < is_val,
        "greater_than": lambda when_value, is_val: when_value > is_val,
    }

    def __init__(
        self,
        is_object,
        when_vos: List[ValueObject],
        then_validators: List[ma.validate.Validator],
        otherwise_validators: List[ma.validate.Validator],
        then_message: str = None,
        otherwise_message: str = None,
        level: str = "error",
        type: str = "int",
        number_dims: int = 0,
    ):
        self.is_operator = next(iter(is_object))
        self.is_val = is_object[self.is_operator]
        self.when_vos = when_vos
        self.then_validators = then_validators
        self.otherwise_validators = otherwise_validators
        self.then_message = then_message or self.then_message
        self.otherwise_message = otherwise_message or self.otherwise_message
        self.level = level
        self.type = type
        self.number_dims = number_dims

    def __call__(self, value, is_value_object=False):
        if value is None:
            return value
        if not is_value_object:
            value = {"value": value}

        msgs = []
        arr = np.array(value["value"])
        for when_vo in self.when_vos:
            if not isinstance(when_vo["value"], list):
                msgs += self.apply_validator(
                    value, when_vo["value"], value, when_vo, ix=None
                )
                continue

            when_arr = np.array(when_vo["value"])
            if when_arr.shape != arr.shape:
                raise ValidationError(
                    self.shape_mismatch.format(
                        shape1=when_arr.shape, shape2=arr.shape
                    )
                )
            for ix in itertools.product(*(map(range, arr.shape))):
                msgs += self.apply_validator(
                    {"value": arr[ix]}, when_arr[ix], value, when_vo, ix
                )

        if msgs:
            raise ValidationError(
                msgs if len(msgs) > 1 else msgs[0], level=self.level
            )

    def evaluate_is_value(self, when_value):
        return self.is_value_evaluators[self.is_operator](
            when_value, self.is_val
        )

    def apply_validator(self, value, when_value, labels, when_labels, ix=None):
        def ix2string(ix):
            return (
                f"[index={', '.join(map(str, ix))}]" if ix is not None else ""
            )

        msgs = []
        is_val_cond = self.evaluate_is_value(when_value)
        if is_val_cond:
            for validator in self.then_validators:
                try:
                    validator(value, is_value_object=True)
                except ValidationError as ve:
                    msgs.append(
                        self.then_message.format(
                            is_val=f"{self.is_operator.replace('_', ' ')} {self.is_val}",
                            submsg=str(ve),
                            labels=utils.make_label_str(labels),
                            when_labels=utils.make_label_str(when_labels),
                            ix=ix2string(ix),
                        )
                    )
        else:
            for validator in self.otherwise_validators:
                try:
                    validator(value, is_value_object=True)
                except ValidationError as ve:
                    msgs.append(
                        self.otherwise_message.format(
                            is_val=f"{self.is_operator.replace('_', ' ')} {self.is_val}",
                            submsg=str(ve),
                            labels=utils.make_label_str(labels),
                            when_labels=utils.make_label_str(when_labels),
                            ix=ix2string(ix),
                        )
                    )
        return msgs

    def grid(self):
        """
        Just return grid of first validator. It's unlikely that
        there will be multiple.
        """
        return self.then_validators[0].grid()

    def cmp_funcs(self, **kwargs):
        return None


class Range(ma.validate.Range):
    """
    Implements "range" :ref:`spec:Validator object`.
    """

    error = ""
    message_min = "Input {input} must be {min_op} {min}."
    message_max = "Input {input} must be {max_op} {max}."

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
                            min_op="greater than",
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
                            max_op="less than",
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

    def cmp_funcs(self, **kwargs):
        return None


class DateRange(Range):
    """
    Implements "date_range" :ref:`spec:Validator object`.
    Behaves like ``Range``, except values are ensured to be
    ``datetime.date`` type and ``grid`` has special logic for dates.
    """

    # check against allowed args:
    # https://docs.python.org/3/library/datetime.html#datetime.timedelta
    timedelta_args = {
        "days",
        "months",
        "seconds",
        "microseconds",
        "milliseconds",
        "minutes",
        "hours",
        "weeks",
    }

    step_msg = (
        f"The step field must be a dictionary with only these keys: {', '.join(timedelta_args)}."
        f"\n\tFor more information, check out the timedelta docs: "
        f"\n\t\thttps://docs.python.org/3/library/datetime.html#datetime.timedelta"
    )

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

        if not isinstance(step, dict):
            raise ValidationError(self.step_msg)

        has_extra_keys = len(set(step.keys()) - self.timedelta_args)
        if has_extra_keys:
            raise ValidationError(self.step_msg)

        self.step = relativedelta(**step)

        self.level = level or "error"

    def safe_deserialize(self, date):
        if isinstance(date, datetime.date):
            return date
        else:
            return ma.fields.Date()._deserialize(date, None, None)

    def grid(self):
        # make np.arange inclusive.
        max_ = self.max[0]["value"] + self.step

        current = self.min[0]["value"]
        result = []
        while current < max_:
            result.append(current)
            current += self.step

        return result


class OneOf(ma.validate.OneOf):
    """
    Implements "choice" :ref:`spec:Validator object`.
    """

    default_message = "Input {input} must be one of {choices}."

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

    def cmp_funcs(self, choices=None, **kwargs):
        if choices is None:
            choices = self.choices
        return {
            "key": lambda x: choices.index(x),
            "gt": lambda x, y: choices.index(x) > choices.index(y),
            "gte": lambda x, y: choices.index(x) >= choices.index(y),
            "lt": lambda x, y: choices.index(x) < choices.index(y),
            "lte": lambda x, y: choices.index(x) <= choices.index(y),
            "ne": lambda x, y: x != y,
            "eq": lambda x, y: x == y,
        }
