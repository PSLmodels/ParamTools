from marshmallow import fields

from paramtools.schema import (
    OrderedSchema,
    BaseValidatorSchema,
    ValueObject,
    get_type,
    get_param_schema,
    ParamToolsSchema,
)
from paramtools import utils


class SchemaFactory:
    """
    Uses data from:
    - a schema definition file
    - a baseline specification file

    to extend:
    - `schema.BaseParamSchema`
    - `schema.BaseValidatorSchema`

    Once this has been completed, the `load_params` method can be used to
    deserialize and validate parameter data.
    """

    def __init__(self, defaults):
        defaults = utils.read_json(defaults)
        self.defaults = {k: v for k, v in defaults.items() if k != "schema"}
        self.schema = ParamToolsSchema().load(defaults.get("schema", {}))
        (self.BaseParamSchema, self.label_validators) = get_param_schema(
            self.schema
        )

    def schemas(self):
        """
        For each parameter defined in the baseline specification file:
        - define a parameter schema for that specific parameter
        - define a validation schema for that specific parameter

        Next, create a baseline specification schema class (`ParamSchema`) for
        all parameters listed in the baseline specification file and a
        validator schema class (`ValidatorSchema`) for all parameters in the
        baseline specification file.

        - `ParamSchema` reads and validates the baseline specification file
        - `ValidatorSchema` reads revisions to the baseline parameters and
          validates their type, structure, and whether they are within the
          specified range.

        `param_schema` is defined and used to read and validate the baseline
        specifications file. `validator_schema` is defined to read and validate
        the parameter revisions. The output from the baseline specification
        deserialization is saved in the `context` attribute on
        `validator_schema` and will be utilized when doing range validation.
        """
        param_dict = {}
        validator_dict = {}
        for k, v in self.defaults.items():
            fieldtype = get_type(v)
            classattrs = {
                "value": fieldtype,
                "_auto": fields.Boolean(required=False, load_only=True),
                **self.label_validators,
            }

            # TODO: what about case where number_dims > 0
            # if not isinstance(v["value"], list):
            #     v["value"] = [{"value": v["value"]}]

            validator_dict[k] = type(
                "ValidatorItem", (OrderedSchema,), classattrs
            )

            classattrs = {"value": ValueObject(validator_dict[k], many=True)}
            param_dict[k] = type(
                "IndividualParamSchema", (self.BaseParamSchema,), classattrs
            )

        classattrs = {k: fields.Nested(v) for k, v in param_dict.items()}
        DefaultsSchema = type("DefaultsSchema", (OrderedSchema,), classattrs)
        defaults_schema = DefaultsSchema()

        classattrs = {
            k: ValueObject(v, many=True) for k, v in validator_dict.items()
        }
        ValidatorSchema = type(
            "ValidatorSchema", (BaseValidatorSchema,), classattrs
        )
        validator_schema = ValidatorSchema()

        return (
            defaults_schema,
            validator_schema,
            self.schema,
            defaults_schema.load(self.defaults),
        )
