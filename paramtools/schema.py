from collections import defaultdict

from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError as MarshmallowValidationError,
    decorators,
)
from marshmallow.error_store import ErrorStore

from paramtools.exceptions import UnknownTypeException, ParamToolsError
from paramtools import contrib
from paramtools import utils
from paramtools import values

fields.Nested = contrib.fields.Nested

ALLOWED_TYPES = ["str", "float", "int", "bool", "date"]


class RangeSchema(Schema):
    """
    Schema for range object
    {
        "range": {"min": field, "max": field}
    }
    """

    _min = fields.Field(attribute="min", data_key="min")
    _max = fields.Field(attribute="max", data_key="max")
    step = fields.Field()
    level = fields.String(validate=[validate.OneOf(["warn", "error"])])


class ChoiceSchema(Schema):
    choices = fields.List(fields.Field)
    level = fields.String(validate=[validate.OneOf(["warn", "error"])])


class ValueValidatorSchema(Schema):
    """
    Schema for validation specification for each parameter value
    """

    _range = fields.Nested(
        RangeSchema(), attribute="range", data_key="range", required=False
    )
    date_range = fields.Nested(RangeSchema(), required=False)
    choice = fields.Nested(ChoiceSchema(), required=False)
    when = fields.Nested("WhenSchema", required=False)


class IsSchema(Schema):
    equal_to = fields.Field(required=False)
    greater_than = fields.Field(required=False)
    less_than = fields.Field(required=False)

    @validates_schema
    def just_one(self, data, **kwargs):
        if len(data.keys()) > 1:
            raise MarshmallowValidationError(
                f"Only one condition may be specified for the 'is' field. "
                f"You specified {len(data.keys())}."
            )

    def _deserialize(self, data, **kwargs):
        if data is not None and not isinstance(data, dict):
            data = {"equal_to": data}
        return super()._deserialize(data, **kwargs)


class WhenSchema(Schema):
    param = fields.Str()
    _is = fields.Nested(
        IsSchema(), attribute="is", data_key="is", required=False
    )
    then = fields.Nested(ValueValidatorSchema())
    otherwise = fields.Nested(ValueValidatorSchema())


class BaseParamSchema(Schema):
    """
    Defines a base parameter schema. This specifies the required fields and
    their types.
    {
        "title": str,
        "description": str,
        "notes": str,
        "type": str (limited to 'int', 'float', 'bool', 'str'),
        "value": `BaseValidatorSchema`, "value" type depends on "type" key,
        "range": range schema ({"min": ..., "max": ..., "other ops": ...}),
    }

    This class is defined further by a JSON file indicating extra fields that
    are required by the implementer of the schema.
    """

    title = fields.Str(required=True)
    description = fields.Str(required=False)
    notes = fields.Str(required=False)
    _type = fields.Str(
        required=True,
        validate=validate.OneOf(choices=ALLOWED_TYPES),
        attribute="type",
        data_key="type",
    )
    number_dims = fields.Integer(required=False, missing=0)
    value = fields.Field(required=True)  # will be specified later
    validators = fields.Nested(
        ValueValidatorSchema(), required=False, missing={}
    )
    indexed = fields.Boolean(required=False)

    class Meta:
        ordered = True


class EmptySchema(Schema):
    """
    An empty schema that is used as a base class for creating other classes via
    the `type` function
    """

    pass


class OrderedSchema(Schema):
    """
    Same as `EmptySchema`, but preserves the order of its fields.
    """

    class Meta:
        ordered = True


class ValueObject(fields.Nested):
    """
    Schema for value objects
    """

    def _validate_missing(self, value):
        """
        If the value is None, this indicates that all of the values
        of the corresponding parameter should be deleted.
        """
        pass

    def _deserialize(
        self, value, attr, data, partial=None, many=False, **kwargs
    ):
        if isinstance(value, values.ValueBase):
            value = list(value)
        if not isinstance(value, list) or (
            isinstance(value, list)
            and value
            and not isinstance(value[0], dict)
        ):
            value = [{"value": value}]
        return super()._deserialize(
            value, attr, data, partial=partial, many=many, **kwargs
        )


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

    class Meta:
        ordered = True

    WRAPPER_MAP = {
        "range": "_get_range_validator",
        "date_range": "_get_range_validator",
        "choice": "_get_choice_validator",
        "when": "_get_when_validator",
    }

    def validate_only(self, data):
        """
        Bypass deserialization and just run field validators. This is taken
        from the marshmallow _do_load function:
        https://github.com/marshmallow-code/marshmallow/blob/3.5.2/src/marshmallow/schema.py#L807
        """
        error_store = ErrorStore()
        # Run field-level validation
        self._invoke_field_validators(
            error_store=error_store, data=data, many=None
        )
        # Run schema-level validation
        if self._has_processors(decorators.VALIDATES_SCHEMA):
            field_errors = bool(error_store.errors)
            self._invoke_schema_validators(
                error_store=error_store,
                pass_many=True,
                data=data,
                original_data=data,
                many=None,
                partial=None,
                field_errors=field_errors,
            )
            self._invoke_schema_validators(
                error_store=error_store,
                pass_many=False,
                data=data,
                original_data=data,
                many=None,
                partial=None,
                field_errors=field_errors,
            )
        errors = error_store.errors
        if errors:
            exc = MarshmallowValidationError(
                errors, data=data, valid_data=data
            )
            self.handle_error(exc, data, many=None, partial=None)
            raise exc
        return data

    def load(self, data, ignore_warnings, deserialized=False):
        self.ignore_warnings = ignore_warnings
        try:
            if deserialized:
                return self.validate_only(data)
            else:
                return super().load(data)
        finally:
            self.ignore_warnings = False

    @validates_schema
    def validate_params(self, data, **kwargs):
        """
        Loop over all parameters defined on this class. Validate them using
        the `self.validate_param`. Errors are stored until all
        parameters have been validated. Note that all data has been
        type-validated. These methods only do range validation.
        """
        warnings = defaultdict(dict)
        errors = defaultdict(dict)
        for name, specs in data.items():
            for i, spec in enumerate(specs):
                _warnings, _errors = self.validate_param(name, spec, data)
                if _warnings:
                    warnings[name][i] = {"value": _warnings}
                if _errors:
                    errors[name][i] = {"value": _errors}
        if warnings and not self.ignore_warnings:
            errors["warnings"] = warnings
        if errors:
            ve = MarshmallowValidationError(dict(errors))
            raise ve

    def validate_param(self, param_name, param_spec, raw_data):
        """
        Do range validation for a parameter.
        """
        validate_schema = not getattr(
            self.context["spec"], "_defer_validation", False
        )
        validators = self.validators(
            param_name, param_spec, raw_data, validate_schema=validate_schema
        )
        warnings = []
        errors = []
        for validator in validators:
            try:
                validator(param_spec, is_value_object=True)
            except contrib.validate.ValidationError as ve:
                if ve.level == "warn":
                    warnings += ve.messages
                else:
                    errors += ve.messages

        return warnings, errors

    def field_keyfunc(self, param_name):
        data = self.context["spec"]._data[param_name]
        field = get_type(data, self.validators(param_name))
        try:
            return field.cmp_funcs()["key"]
        except AttributeError:
            return None

    def field(self, param_name):
        data = self.context["spec"]._data[param_name]
        return get_type(data, self.validators(param_name))

    def validators(
        self, param_name, param_spec=None, raw_data=None, validate_schema=True
    ):
        if param_spec is None:
            param_spec = {}
        if raw_data is None:
            raw_data = {}

        param_info = self.context["spec"]._data[param_name]
        # sort keys to guarantee order.
        validator_spec = param_info.get("validators", {})
        validators = []
        for vname, vdata in validator_spec.items():
            if vname == "range" and param_info.get("type", None) in ("date",):
                vname = "date_range"
            validator = getattr(self, self.WRAPPER_MAP[vname])(
                vname,
                vdata,
                param_name,
                param_spec,
                raw_data,
                validate_schema=validate_schema,
            )
            validators.append(validator)
        return validators

    def _get_when_validator(
        self,
        vname,
        when_dict,
        param_name,
        param_spec,
        raw_data,
        ndim_restriction=False,
        validate_schema=True,
    ):
        if not validate_schema:
            return
        when_param = when_dict["param"]

        if (
            when_param not in self.context["spec"]._data.keys()
            and when_param != "default"
        ):
            raise MarshmallowValidationError(
                f"'{when_param}' is not a specified parameter."
            )

        oth_param, when_vos = self._get_related_value(
            when_param, param_name, param_spec, raw_data
        )
        then_validators = []
        for vname, vdata in when_dict["then"].items():
            then_validators.append(
                getattr(self, self.WRAPPER_MAP[vname])(
                    vname,
                    vdata,
                    param_name,
                    param_spec,
                    raw_data,
                    ndim_restriction=True,
                )
            )
        otherwise_validators = []
        for vname, vdata in when_dict["otherwise"].items():
            otherwise_validators.append(
                getattr(self, self.WRAPPER_MAP[vname])(
                    vname,
                    vdata,
                    param_name,
                    param_spec,
                    raw_data,
                    ndim_restriction=True,
                )
            )

        _type = self.context["spec"]._data[oth_param]["type"]
        number_dims = self.context["spec"]._data[oth_param]["number_dims"]

        error_then = (
            f"When {oth_param}{{when_labels}}{{ix}} is {{is_val}}, "
            f"{param_name}{{labels}}{{ix}} value is invalid: {{submsg}}"
        )
        error_otherwise = (
            f"When {oth_param}{{when_labels}}{{ix}} is not {{is_val}}, "
            f"{param_name}{{labels}}{{ix}} value is invalid: {{submsg}}"
        )

        return contrib.validate.When(
            when_dict["is"],
            when_vos,
            then_validators,
            otherwise_validators,
            error_then,
            error_otherwise,
            _type,
            number_dims,
        )

    def _get_range_validator(
        self,
        vname,
        range_dict,
        param_name,
        param_spec,
        raw_data,
        ndim_restriction=False,
        validate_schema=True,
    ):
        if vname == "range":
            range_class = contrib.validate.Range
        elif vname == "date_range":
            range_class = contrib.validate.DateRange
        else:
            raise MarshmallowValidationError(
                f"{vname} is not an allowed validator."
            )
        min_value = range_dict.get("min", None)
        is_related_param = min_value == "default" or min_value in self.fields
        if min_value is None or (is_related_param and not validate_schema):
            min_oth_param, min_vos = None, []
        elif is_related_param and validate_schema:
            min_oth_param, min_vos = self._get_related_value(
                min_value, param_name, param_spec, raw_data
            )
        else:
            min_oth_param, min_vos = None, [{"value": min_value}]

        max_value = range_dict.get("max", None)
        is_related_param = max_value == "default" or max_value in self.fields
        if max_value is None or (is_related_param and not validate_schema):
            max_oth_param, max_vos = None, []
        elif is_related_param and validate_schema:
            max_oth_param, max_vos = self._get_related_value(
                max_value, param_name, param_spec, raw_data
            )
        else:
            max_oth_param, max_vos = None, [{"value": max_value}]
        self._check_ndim_restriction(
            param_name,
            min_oth_param,
            max_oth_param,
            ndim_restriction=ndim_restriction,
        )
        min_vos = self._sort_by_label_to_extend(min_vos)
        max_vos = self._sort_by_label_to_extend(max_vos)
        error_min = (
            f"{param_name}{{labels}} {{input}} < min {{min}} "
            f"{min_oth_param or ''}{{oth_labels}}"
        ).strip()
        error_max = (
            f"{param_name}{{labels}} {{input}} > max {{max}} "
            f"{max_oth_param or ''}{{oth_labels}}"
        ).strip()
        return range_class(
            min_vo=min_vos,
            max_vo=max_vos,
            error_min=error_min,
            error_max=error_max,
            level=range_dict.get("level"),
        )

    def _sort_by_label_to_extend(self, vos):
        label_to_extend = self.context["spec"].label_to_extend
        if label_to_extend is not None:
            label_grid = self.context["spec"]._stateless_label_grid
            extend_vals = label_grid[label_to_extend]
            return sorted(
                vos,
                key=lambda vo: (
                    extend_vals.index(vo[label_to_extend])
                    if label_to_extend in vo
                    and vo[label_to_extend] in extend_vals
                    else 9e99
                ),
            )
        else:
            return vos

    def _get_choice_validator(
        self,
        vname,
        choice_dict,
        param_name,
        param_spec,
        raw_data,
        ndim_restriction=False,
        validate_schema=True,
    ):
        choices = choice_dict["choices"]
        labels = utils.make_label_str(param_spec)
        label_suffix = f" for labels {labels}" if labels else ""
        if len(choices) < 20:
            error_template = (
                '{param_name} "{input}" must be in list of choices '
                "{choices}{label_suffix}."
            )
        else:
            error_template = '{param_name} "{input}" must be in list of choices{label_suffix}.'
        error = error_template.format(
            param_name=param_name,
            labels=labels,
            input="{input}",
            choices="{choices}",
            label_suffix=label_suffix,
        )
        return contrib.validate.OneOf(
            choices, error=error, level=choice_dict.get("level")
        )

    def _get_related_value(
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
                oth_param = self.context["spec"]._data[param_name]
            else:
                oth_param = self.context["spec"]._data[oth_param_name]
            vals = oth_param["value"]
        labs_to_check = {k for k in param_spec if k not in ("value", "_auto")}
        if labs_to_check:
            res = [
                val
                for val in vals
                if all(val[k] == param_spec[k] for k in labs_to_check)
            ]
        else:
            res = vals
        return oth_param_name, res

    def _check_ndim_restriction(
        self, param_name, *other_params, ndim_restriction=False
    ):
        """
        Test restriction on validator's concerning references to other
        parameters with number of dimensions >= 1.
        """
        if ndim_restriction and any(other_params):
            for other_param in other_params:
                if other_param is None:
                    continue
                if other_param == "default":
                    ndims = self.context["spec"]._data[param_name][
                        "number_dims"
                    ]
                else:
                    ndims = self.context["spec"]._data[other_param][
                        "number_dims"
                    ]
                if ndims > 0:
                    raise contrib.validate.ValidationError(
                        f"{param_name} is validated against {other_param} in an invalid context."
                    )


class LabelSchema(Schema):
    _type = fields.Str(
        required=True,
        validate=validate.OneOf(choices=ALLOWED_TYPES),
        attribute="type",
        data_key="type",
    )
    number_dims = fields.Integer(required=False, missing=0)
    validators = fields.Nested(
        ValueValidatorSchema(), required=False, missing={}
    )


def make_additional_members(allowed_types):
    class AdditionalMembersSchema(Schema):
        _type = fields.Str(
            required=True,
            validate=validate.OneOf(choices=allowed_types),
            attribute="type",
            data_key="type",
        )
        number_dims = fields.Integer(required=False, missing=0)

    return AdditionalMembersSchema


class OperatorsSchema(Schema):
    array_first = fields.Bool(required=False)
    label_to_extend = fields.Str(required=False, allow_none=True)
    uses_extend_func = fields.Bool(required=False)


def make_schema(allowed_types):
    class ParamToolsSchema(Schema):
        labels = fields.Dict(
            keys=fields.Str(),
            values=fields.Nested(LabelSchema()),
            required=False,
            missing={},
        )
        additional_members = fields.Dict(
            keys=fields.Str(),
            values=fields.Nested(make_additional_members(allowed_types)()),
            required=False,
            missing={},
        )
        operators = fields.Nested(OperatorsSchema, required=False)

    return ParamToolsSchema


def is_field_class_like(field):
    if isinstance(field, type) and issubclass(field, fields.FieldABC):
        return True
    elif isinstance(field, PartialField):
        return True
    else:
        return False


def is_field_instance_like(field):
    if not isinstance(field, type) and isinstance(field, fields.Field):
        return True
    else:
        return False


def register_custom_type(name: str, field: fields.Field):
    if isinstance(field, type):
        raise TypeError(
            f"Custom fields must be instances. {field} is a class."
        )
    elif not isinstance(field, PartialField) and not is_field_instance_like(
        field
    ):
        raise TypeError(
            "Custom fields must either be instances of PartialField or a marshmallow field."
        )
    ALLOWED_TYPES.append(name)
    FIELD_MAP.update({name: field})


ParamToolsSchema = make_schema(allowed_types=ALLOWED_TYPES)


INVALID_NUMBER = {"invalid": "Not a valid number: {input}."}
INVALID_INTEGER = {"invalid": "Not a valid integer: {input}."}
INVALID_BOOLEAN = {"invalid": "Not a valid boolean: {input}."}
INVALID_DATE = {"invalid": "Not a valid date: {input}."}


class PartialField:
    def __init__(self, field, default_kwargs=None):
        self.field = field
        self.default_kwargs = default_kwargs or {}

    def __call__(self, **kwargs):
        return self.field(**dict(self.default_kwargs, **kwargs))


# A few fields that have been instantiated
FIELD_MAP = {
    "str": PartialField(contrib.fields.Str, dict(allow_none=True)),
    "int": PartialField(
        contrib.fields.Integer,
        dict(allow_none=True, error_messages=INVALID_INTEGER),
    ),
    "float": PartialField(
        contrib.fields.Float,
        dict(allow_none=True, error_messages=INVALID_NUMBER),
    ),
    "bool": PartialField(
        contrib.fields.Boolean,
        dict(allow_none=True, error_messages=INVALID_BOOLEAN),
    ),
    "date": PartialField(
        contrib.fields.Date, dict(allow_none=True, error_messages=INVALID_DATE)
    ),
}

VALIDATOR_MAP = {
    "range": contrib.validate.Range,
    "date_range": contrib.validate.DateRange,
    "choice": contrib.validate.OneOf,
}


def get_type(data, validators=None):
    numeric_types = {
        "int": contrib.fields.Int64(
            allow_none=True, error_messages=INVALID_INTEGER, strict=True
        ),
        "bool": contrib.fields.Bool_(
            allow_none=True, error_messages=INVALID_BOOLEAN
        ),
        "float": contrib.fields.Float64(
            allow_none=True, error_messages=INVALID_NUMBER
        ),
    }
    types = dict(FIELD_MAP, **numeric_types)
    try:
        _fieldtype = types[data["type"]]
        if is_field_class_like(_fieldtype):
            fieldtype = _fieldtype(validate=validators)
        elif is_field_instance_like(_fieldtype):
            fieldtype = _fieldtype
        else:
            raise TypeError("Field is invalid.")
    except KeyError:
        raise UnknownTypeException(
            f"Received unknown type: {data['type']}. Expected one of {', '.join(ALLOWED_TYPES)}."
        )
    dim = data.get("number_dims", 0)
    while dim > 0:
        np_type = getattr(fieldtype, "np_type", object)
        fieldtype = fields.List(fieldtype, allow_none=True)
        fieldtype.np_type = np_type
        dim -= 1
    return fieldtype


def get_param_schema(base_spec):
    """
    Read in data from the initializing schema. This will be used to fill in the
    optional properties on classes derived from the `BaseParamSchema` class.
    This data is also used to build validators for schema for each parameter
    that will be set on the `BaseValidatorSchema` class
    """
    field_map = FIELD_MAP
    optional_fields = {}
    for k, v in base_spec["additional_members"].items():
        try:
            # in the future, we may want to allow validators.
            _fieldtype = field_map[v["type"]]
            if is_field_class_like(_fieldtype):
                fieldtype = _fieldtype()
            elif is_field_instance_like(_fieldtype):
                fieldtype = _fieldtype
            else:
                raise TypeError("Field is invalid.")
        except KeyError:
            raise UnknownTypeException(
                f"Received unknown type: {v['type']}. Expected one of {', '.join(ALLOWED_TYPES)}."
            )
        if v.get("number_dims", 0) > 0:
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
    label_validators = {}
    for name, label in base_spec["labels"].items():
        validators = []
        for vname, kwargs in label.get("validators", {}).items():
            if vname == "range" and label.get("type", None) in ("date",):
                vname = "date_range"

            validator_class = VALIDATOR_MAP[vname]
            validators.append(validator_class(**kwargs))
        try:
            _fieldtype = field_map[label["type"]]
            if is_field_class_like(_fieldtype):
                fieldtype = _fieldtype(validate=validators)
            elif validators:
                raise ParamToolsError(
                    "If a field is already initialized, then it cannot define "
                    "its validators via JSON configuration. You should use "
                    "PartialField if you want to define validators via JSON."
                )
            elif is_field_instance_like(_fieldtype):
                fieldtype = _fieldtype
            else:
                raise TypeError("Field is invalid.")

            label_validators[name] = fieldtype

        except KeyError:
            raise UnknownTypeException(
                f"Received unknown type: {label['type']}. Expected one of "
                f"{', '.join(ALLOWED_TYPES)}."
            )

    return ParamSchema, label_validators
