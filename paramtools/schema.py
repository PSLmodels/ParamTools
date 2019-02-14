from collections import defaultdict

import numpy as np
from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError as MarshmallowValidationError,
)

from paramtools.contrib import (
    validate as contrib_validate,
    fields as contrib_fields,
)


class RangeSchema(Schema):
    """
    Schema for range object
    {
        "range": {"min": field, "max": field}
    }
    """

    _min = fields.Field(attribute="min", data_key="min")
    _max = fields.Field(attribute="max", data_key="max")


class ChoiceSchema(Schema):
    choices = fields.List(fields.Field)


class ValueValidatorSchema(Schema):
    """
    Schema for validation specification for each parameter value
    """

    _range = fields.Nested(
        RangeSchema(), attribute="range", data_key="range", required=False
    )
    date_range = fields.Nested(RangeSchema(), required=False)
    choice = fields.Nested(ChoiceSchema(), required=False)


class BaseParamSchema(Schema):
    """
    Defines a base parameter schema. This specifies the required fields and
    their types.
    {
        "title": str,
        "description": str,
        "notes": str,
        "type": str (limited to 'int', 'float', 'bool', 'str'),
        "number_dims": int,
        "value": `BaseValidatorSchema`, "value" type depends on "type" key,
        "range": range schema ({"min": ..., "max": ..., "other ops": ...}),
        "out_of_range_minmsg": str,
        "out_of_range_maxmsg": str,
        "out_of_range_action": str (limited to 'stop' or 'warn')
    }

    This class is defined further by a JSON file indicating extra fields that
    are required by the implementer of the schema.
    """

    title = fields.Str(required=True)
    description = fields.Str(required=True)
    notes = fields.Str(required=True)
    _type = fields.Str(
        required=True,
        validate=validate.OneOf(
            choices=["str", "float", "int", "bool", "date"]
        ),
        attribute="type",
        data_key="type",
    )
    number_dims = fields.Integer(required=True)
    value = fields.Field(required=True)  # will be specified later
    validators = fields.Nested(ValueValidatorSchema(), required=True)
    out_of_range_minmsg = fields.Str()
    out_of_range_maxmsg = fields.Str()
    out_of_range_action = fields.Str(
        required=False, validate=validate.OneOf(choices=["stop", "warn"])
    )


class EmptySchema(Schema):
    """
    An empty schema that is used as a base class for creating other classes via
    the `type` function
    """

    pass


class BaseValidatorSchema(Schema):
    """
    Schema that validates parameter adjustments such as:
    ```
    {
        "STD": [{
            "year": 2017,
            "MARS": "single",
            "value": "3000"
        }]
    }
    ```

    Information defined for each variable on the `BaseParamSchema` is utilized
    to define this class and how it should validate its data. See
    `build_schema.SchemaBuilder` for how parameters are defined onto this
    class.
    """

    WRAPPER_MAP = {
        "range": "_get_range_validator",
        "date_range": "_get_range_validator",
        "choice": "_get_choice_validator",
    }

    @validates_schema
    def validate_params(self, data):
        """
        Loop over all parameters defined on this class. Validate them using
        the `self.validate_param`. Errors are stored until all
        parameters have been validated. Note that all data has been
        type-validated. These methods only do range validation.
        """
        errors = defaultdict(dict)
        errors_exist = False
        for name, specs in data.items():
            for i, spec in enumerate(specs):
                iserrors = self.validate_param(name, spec, data)
                if iserrors:
                    errors_exist = True
                    errors[name][i] = {"value": iserrors}
        if errors_exist:
            raise MarshmallowValidationError(dict(errors))

    def validate_param(self, param_name, param_spec, raw_data):
        """
        Do range validation for a parameter.
        """
        param_info = self.context["spec"]._data[param_name]
        # sort keys to guarantee order.
        dims = " , ".join(
            [
                f"{k}={param_spec[k]}"
                for k in sorted(param_spec)
                if k != "value"
            ]
        )
        validator_spec = param_info["validators"]
        validators = []
        for validator_name, method_name in self.WRAPPER_MAP.items():
            if validator_name in validator_spec:
                validator = getattr(self, method_name)(
                    validator_name,
                    validator_spec[validator_name],
                    param_name,
                    dims,
                    param_spec,
                    raw_data,
                )
                validators.append(validator)

        value = param_spec["value"]
        errors = []
        for validator in validators:
            try:
                validator(value)
            except MarshmallowValidationError as ve:
                errors.append(str(ve))

        return errors

    def _get_range_validator(
        self, vname, range_dict, param_name, dims, param_spec, raw_data
    ):
        if vname == "range":
            range_class = contrib_validate.Range
        elif vname == "date_range":
            range_class = contrib_validate.DateRange
        else:
            raise MarshmallowValidationError(
                f"{vname} is not an allowed validator"
            )
        min_value = range_dict.get("min", None)
        if min_value is not None:
            min_value = self._resolve_op_value(
                min_value, param_name, param_spec, raw_data
            )
        max_value = range_dict.get("max", None)
        if max_value is not None:
            max_value = self._resolve_op_value(
                max_value, param_name, param_spec, raw_data
            )
        min_error = (
            "{param_name} {input} must be greater than "
            "{min} for dimensions {dims}"
        ).format(
            param_name=param_name, dims=dims, input="{input}", min="{min}"
        )
        max_error = (
            "{param_name} {input} must be less than "
            "{max} for dimensions {dims}"
        ).format(
            param_name=param_name, dims=dims, input="{input}", max="{max}"
        )
        return range_class(min_value, max_value, min_error, max_error)

    def _get_choice_validator(
        self, vname, choice_dict, param_name, dims, param_spec, raw_data
    ):
        choices = choice_dict["choices"]
        if len(choices) < 20:
            error_template = (
                '{param_name} "{input}" must be in list of choices '
                "{choices} for dimensions {dims}."
            )
        else:
            error_template = (
                '{param_name} "{input}" must be in list of choices '
                "for dimensions {dims}."
            )
        error = error_template.format(
            param_name=param_name,
            dims=dims,
            input="{input}",
            choices="{choices}",
        )
        return contrib_validate.OneOf(choices, error=error)

    def _resolve_op_value(self, op_value, param_name, param_spec, raw_data):
        """
        Operator values (`op_value`) are the values pointed to by the "min"
        and "max" keys. These can be values to compare against, another
        variable to compare against, or the default value of the adjusted
        variable.
        """
        if op_value in self.fields or op_value == "default":
            return self._get_comparable_value(
                op_value, param_name, param_spec, raw_data
            )
        return op_value

    def _get_comparable_value(
        self, oth_param_name, param_name, param_spec, raw_data
    ):
        """
        Get the value that the adjusted variable will be compared against.
        Candidates are:
        - the parameter's own default value if "default" is specified
        - a reference variable's value
          - first, look in the raw adjustment data
          - second, look in the defaults data
        """
        if oth_param_name in raw_data:
            vals = raw_data[oth_param_name]
        else:
            # If comparing against the "default" value then get the current
            # value of the parameter being updated.
            if oth_param_name == "default":
                oth_param_name = param_name
            oth_param = self.context["spec"]._data[oth_param_name]
            vals = oth_param["value"]
        dims_to_check = tuple(k for k in param_spec if k != "value")
        res = [
            val
            for val in vals
            if all(val[k] == param_spec[k] for k in dims_to_check)
        ]
        assert len(res) == 1
        return res[0]["value"]


# A few fields that have not been instantiated yet
CLASS_FIELD_MAP = {
    "str": contrib_fields.Str,
    "int": contrib_fields.Integer,
    "float": contrib_fields.Float,
    "bool": contrib_fields.Boolean,
    "date": contrib_fields.Date,
}


# A few fields that have been instantiated
FIELD_MAP = {
    "str": contrib_fields.Str(),
    "int": contrib_fields.Integer(),
    "float": contrib_fields.Float(),
    "bool": contrib_fields.Boolean(),
    "date": contrib_fields.Date(),
}

VALIDATOR_MAP = {
    "range": contrib_validate.Range,
    "date_range": contrib_validate.DateRange,
    "choice": contrib_validate.OneOf,
}


def get_type(data):
    # TODO: Use invalid error messages on next marshmallow release
    # (post 0.3.0rc4)
    # error_messages = {"invalid": "Invalid input: {input}"}
    numeric_types = {
        "int": contrib_fields.Int64(),
        "bool": contrib_fields.Bool_(),
        "float": contrib_fields.Float64(),
    }
    types = dict(FIELD_MAP, **numeric_types)
    fieldtype = types[data["type"]]
    dim = data["number_dims"]
    while dim > 0:
        fieldtype = fields.List(fieldtype)
        dim -= 1
    return fieldtype


def get_param_schema(base_spec, field_map=None):
    """
    Read in data from the initializing schema. This will be used to fill in the
    optional properties on classes derived from the `BaseParamSchema` class.
    This data is also used to build validators for schema for each parameter
    that will be set on the `BaseValidatorSchema` class
    """
    if field_map is not None:
        field_map = dict(FIELD_MAP, **field_map)
    else:
        field_map = FIELD_MAP.copy()
    optional_fields = {}
    for k, v in base_spec["optional"].items():
        fieldtype = field_map[v["type"]]
        if v["number_dims"] is not None:
            d = v["number_dims"]
            while d > 0:
                fieldtype = fields.List(fieldtype)
                d -= 1
        optional_fields[k] = fieldtype

    ParamSchema = type(
        "ParamSchema",
        (BaseParamSchema,),
        {k: v for k, v in optional_fields.items()},
    )
    dim_validators = {}
    for name, dim in base_spec["dims"].items():
        validators = []
        for vname, kwargs in dim["validators"].items():
            validator_class = VALIDATOR_MAP[vname]
            validators.append(validator_class(**kwargs))
        fieldtype = CLASS_FIELD_MAP[dim["type"]]
        dim_validators[name] = fieldtype(validate=validators)
    return ParamSchema, dim_validators
